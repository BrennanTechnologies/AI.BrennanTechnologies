# Author:  Chris Brennan
# Company: Brennan Technologies, LLC
# Email:   chris@brennantechnologies.com
# Web:     https://www.brennantechnologies.com

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

from app.config import Settings


def _get_credential(settings: Settings):
    if settings.azure_search_api_key:
        return AzureKeyCredential(settings.azure_search_api_key)
    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def get_index_client(settings: Settings) -> SearchIndexClient:
    return SearchIndexClient(endpoint=settings.azure_search_endpoint, credential=_get_credential(settings))


def get_search_client(settings: Settings) -> SearchClient:
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_name,
        credential=_get_credential(settings),
    )


def ensure_index(settings: Settings, vector_dimensions: int = 3072) -> None:
    index_client = get_index_client(settings)

    try:
        index_client.get_index(settings.azure_search_index_name)
        return
    except Exception:
        pass

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchableField(name="filename", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, filterable=True, sortable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=vector_dimensions,
            vector_search_profile_name="default-vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
        profiles=[VectorSearchProfile(name="default-vector-profile", algorithm_configuration_name="default-hnsw")],
    )

    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="default-semantic",
                prioritized_fields=SemanticPrioritizedFields(content_fields=[SemanticField(field_name="content")]),
            )
        ]
    )

    index = SearchIndex(
        name=settings.azure_search_index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )
    index_client.create_or_update_index(index)
