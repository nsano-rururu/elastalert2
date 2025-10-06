# -*- coding: utf-8 -*-
"""
Compatibility layer for elasticsearch-py and opensearch-py.

This module allows ElastAlert2 to work with either elasticsearch-py or opensearch-py
by providing a unified interface for importing the necessary components.

Users can install either:
- elasticsearch==7.10.1 (default, for Elasticsearch)
- opensearch-py (for OpenSearch)

The module will automatically detect which library is available and use it.
"""

# Try to import from elasticsearch-py first (default)
try:
    from elasticsearch import Elasticsearch
    from elasticsearch import RequestsHttpConnection
    from elasticsearch.client import _make_path
    from elasticsearch.client import query_params
    from elasticsearch.client import IndicesClient
    from elasticsearch.exceptions import (
        TransportError,
        ConnectionError,
        ElasticsearchException,
        NotFoundError
    )
    import elasticsearch.helpers as helpers
    
    # Flag to indicate which library is being used
    USING_OPENSEARCH = False
    
except ImportError:
    # Fall back to opensearch-py if elasticsearch-py is not available
    try:
        from opensearchpy import OpenSearch as Elasticsearch
        from opensearchpy import RequestsHttpConnection
        from opensearchpy.client import _make_path
        from opensearchpy.client import query_params
        from opensearchpy.client import IndicesClient
        from opensearchpy.exceptions import (
            TransportError,
            ConnectionError,
            OpenSearchException as ElasticsearchException,
            NotFoundError
        )
        import opensearchpy.helpers as helpers
        
        # Flag to indicate which library is being used
        USING_OPENSEARCH = True
        
    except ImportError:
        raise ImportError(
            "Either elasticsearch-py or opensearch-py must be installed. "
            "Install one of them using:\n"
            "  pip install elasticsearch==7.10.1  (for Elasticsearch)\n"
            "  pip install opensearch-py  (for OpenSearch)"
        )

# Export all the required components
__all__ = [
    'Elasticsearch',
    'RequestsHttpConnection',
    'IndicesClient',
    '_make_path',
    'query_params',
    'TransportError',
    'ConnectionError',
    'ElasticsearchException',
    'NotFoundError',
    'helpers',
    'USING_OPENSEARCH',
]
