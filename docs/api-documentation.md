# REST API Documentation - Version 1

## Base API URL

`http://`*server_hostname*`/api/v1/`

## **Endpoints**

### Endpoint name: `traits/`

The v1 API's single endpoint, provided information about a trait and its current mapping.
### Allowed methods: [ `GET` ]

### Filters:
- `status`: Each trait mapping can have one of the following status values to filter by:
    + `current`
    + `unmapped`
    + `obsolete`
    + `deleted`
    + `needs_import`
    + `awaiting_import`
    + `needs_creation`
    + `awaiting_creation`
    + `awaiting_review`
- `name`: Filter by fuzzy searching in the trait name

### Examples:

#### Get all traits:

```
curl http://server_hostname/api/v1/traits/
```
<details>
<summary>Example response:</summary>

``` json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "trait_id": 296,
      "name": "/ Spastic paraplegia /",
      "current_mapping": null,
      "status": "unmapped",
      "number_of_source_records": 7
    },
    {
      "trait_id": 291,
      "name": "/ pancreatic cancer, susceptibility to, 4 /",
      "current_mapping": {
        "mapping_id": 65,
        "mapped_term": {
          "term_id": 108,
          "curie": "MONDO:0013685",
          "iri": "http://purl.obolibrary.org/obo/MONDO_0013685",
          "label": "/ pancreatic cancer, susceptibility to, 4 /",
          "status": "awaiting_import",
          "description": null,
          "cross_refs": null
        },
        "is_reviewed": true
      },
      "status": "awaiting_import",
      "number_of_source_records": 5
    },
    {
      "trait_id": 293,
      "name": "/ Pancreatic cancer 4 /",
      "current_mapping": {
        "mapping_id": 67,
        "mapped_term": {
          "term_id": 110,
          "curie": null,
          "iri": null,
          "label": "/ Familial cancer of breast, 2 /",
          "status": "awaiting_creation",
          "description": "Description for familial cancer of breast, 2",
          "cross_refs": "Orphanet:0000405"
        },
        "is_reviewed": true
      },
      "status": "awaiting_creation",
      "number_of_source_records": 1
    }
  ]
}
```
</details>


#### Get all traits with 'awaiting_review' status:
```
curl http://server_hostname/api/v1/traits/?status=current
```

<details>
<summary>Example response:</summary>

``` json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "trait_id": 298,
      "name": "/ digestive system disease /",
      "current_mapping": {
        "mapping_id": 72,
        "mapped_term": {
          "term_id": 115,
          "curie": "EFO:0000405",
          "iri": "http://www.ebi.ac.uk/efo/EFO_0000405",
          "label": "/ digestive system disease /",
          "status": "current",
          "description": null,
          "cross_refs": null
        },
        "is_reviewed": false
      },
      "status": "awaiting_review",
      "number_of_source_records": 4
    },
    {
      "trait_id": 300,
      "name": "/ Insulin-resistant diabetes mellitus /",
      "current_mapping": {
        "mapping_id": 74,
        "mapped_term": {
          "term_id": 117,
          "curie": "MONDO:0013253",
          "iri": "http://purl.obolibrary.org/obo/MONDO_0013253",
          "label": "/ breast-ovarian cancer, familial, susceptibility to, 3 /",
          "status": "needs_import",
          "description": null,
          "cross_refs": null
        },
        "is_reviewed": false
      },
      "status": "awaiting_review",
      "number_of_source_records": 1
    },
    {
      "trait_id": 303,
      "name": "/ Pancreatic cancer 4 /",
      "current_mapping": {
        "mapping_id": 77,
        "mapped_term": {
          "term_id": 120,
          "curie": null,
          "iri": null,
          "label": "/ Familial cancer of breast, 2 /",
          "status": "awaiting_creation",
          "description": "Description for familial cancer of breast, 2",
          "cross_refs": "Orphanet:0000405"
        },
        "is_reviewed": false
      },
      "status": "awaiting_review",
      "number_of_source_records": 1
    }
  ]
}
```
</details>

#### Get all traits with 'current' status and 'diabetes' in their name:
```
curl http://server_hostname/api/v1/traits/?status=current&name=diabetes
```

<details>
<summary>Example response:</summary>

``` json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "trait_id": 51,
      "name": "/ Diabetes mellitus /",
      "current_mapping": {
        "mapping_id": 52,
        "mapped_term": {
          "term_id": 95,
          "curie": "EFO:0000400",
          "iri": "http://www.ebi.ac.uk/efo/EFO_0000400",
          "label": "/ Diabetes mellitus /",
          "status": "current",
          "description": null,
          "cross_refs": null
        },
        "is_reviewed": true
      },
      "status": "current",
      "number_of_source_records": 9
    }
  ]
}
```
</details>
