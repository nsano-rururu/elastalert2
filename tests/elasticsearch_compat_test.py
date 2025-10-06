# -*- coding: utf-8 -*-
"""
Tests for elasticsearch_compat module to ensure it correctly handles
both elasticsearch-py and opensearch-py imports.
"""
import pytest
import sys
from unittest import mock


def test_elasticsearch_compat_imports():
    """Test that all required imports are available through the compatibility layer."""
    from elastalert.elasticsearch_compat import (
        Elasticsearch,
        RequestsHttpConnection,
        IndicesClient,
        _make_path,
        query_params,
        TransportError,
        ConnectionError,
        ElasticsearchException,
        NotFoundError,
        helpers,
        USING_OPENSEARCH,
    )

    # Verify all imports are not None
    assert Elasticsearch is not None
    assert RequestsHttpConnection is not None
    assert IndicesClient is not None
    assert _make_path is not None
    assert query_params is not None
    assert TransportError is not None
    assert ConnectionError is not None
    assert ElasticsearchException is not None
    assert NotFoundError is not None
    assert helpers is not None
    assert isinstance(USING_OPENSEARCH, bool)


def test_elasticsearch_compat_with_elasticsearch_py():
    """Test that when elasticsearch-py is available, it's used."""
    from elastalert.elasticsearch_compat import USING_OPENSEARCH, Elasticsearch

    # When elasticsearch-py is installed (as in our current test environment)
    # USING_OPENSEARCH should be False
    assert USING_OPENSEARCH is False

    # The class name should be Elasticsearch
    assert Elasticsearch.__name__ == 'Elasticsearch'


def test_elastalert_client_uses_compat_layer():
    """Test that ElasticSearchClient properly uses the compatibility layer."""
    from elastalert import ElasticSearchClient
    from elastalert.elasticsearch_compat import Elasticsearch

    # ElasticSearchClient should be a subclass of the Elasticsearch class
    # from the compatibility layer
    assert issubclass(ElasticSearchClient, Elasticsearch)


def test_compatibility_layer_in_util():
    """Test that util module uses the compatibility layer."""
    from elastalert import util

    # Just importing should work without errors
    # This verifies that util.py successfully imports TransportError
    # from the compatibility layer
    assert hasattr(util, 'TransportError')


def test_compatibility_layer_in_create_index():
    """Test that create_index module uses the compatibility layer."""
    from elastalert import create_index

    # Just importing should work without errors
    # This verifies that create_index.py successfully imports all needed
    # components from the compatibility layer
    assert hasattr(create_index, 'Elasticsearch')
    assert hasattr(create_index, 'IndicesClient')


def test_compatibility_layer_in_elastalert():
    """Test that elastalert module uses the compatibility layer."""
    from elastalert import elastalert

    # Just importing should work without errors
    # This verifies that elastalert.py successfully imports exceptions
    # from the compatibility layer
    assert hasattr(elastalert, 'ConnectionError')
    assert hasattr(elastalert, 'TransportError')


def test_opensearch_detection_still_works():
    """Test that OpenSearch detection in util.py still works correctly."""
    from elastalert.util import get_version_from_cluster_info
    from unittest.mock import MagicMock

    # Mock a client that returns OpenSearch 2.0.0
    mock_client = MagicMock()
    mock_client.info.return_value = {
        'version': {
            'number': '2.0.0',
            'distribution': 'opensearch'
        }
    }

    version = get_version_from_cluster_info(mock_client)

    # OpenSearch 2.x should be mapped to 8.2.0
    assert version == '8.2.0'


def test_opensearch_py_fallback_error_message():
    """Test that a helpful error message is shown when neither library is available."""
    # Save the original modules
    original_elasticsearch = sys.modules.get('elasticsearch')
    original_opensearchpy = sys.modules.get('opensearchpy')

    # Remove both modules from sys.modules to simulate neither being installed
    if 'elasticsearch' in sys.modules:
        del sys.modules['elasticsearch']
    if 'opensearchpy' in sys.modules:
        del sys.modules['opensearchpy']

    # Also need to remove the compat module so it re-imports
    if 'elastalert.elasticsearch_compat' in sys.modules:
        del sys.modules['elastalert.elasticsearch_compat']

    try:
        # Mock the import to raise ImportError for both libraries
        with mock.patch.dict('sys.modules', {
            'elasticsearch': None,
            'opensearchpy': None,
            'elasticsearch.client': None,
            'elasticsearch.exceptions': None,
            'elasticsearch.helpers': None,
            'opensearchpy.client': None,
            'opensearchpy.exceptions': None,
            'opensearchpy.helpers': None,
        }):
            with pytest.raises(ImportError) as exc_info:
                # This import should fail with a helpful message
                import importlib
                if 'elastalert.elasticsearch_compat' in sys.modules:
                    del sys.modules['elastalert.elasticsearch_compat']
                importlib.import_module('elastalert.elasticsearch_compat')

            # Check that the error message is helpful
            error_message = str(exc_info.value)
            assert 'elasticsearch-py' in error_message or 'opensearch-py' in error_message
    finally:
        # Restore the original modules
        if original_elasticsearch:
            sys.modules['elasticsearch'] = original_elasticsearch
        if original_opensearchpy:
            sys.modules['opensearchpy'] = original_opensearchpy
