# ACAI Account-Cache-Query Documentation <a id="top">
<!-- LOGO -->
<a href="https://acai.gmbh">
    <img src="https://acai.gmbh/images/logo/logo-acai-badge.png" alt="acai logo" title="acai" align="right" width="100" />
</a>

<!-- SHIELDS -->
[![Maintained by acai.gmbh][acai-shield]][acai-url] ![Copyright by acai.gmbh][acai-copyright-shield]

This documentation focuses on how to query the ACAI ACF Account Cache, and provides guidelines and examples for specifying Query JSONs to select specific AWS accounts from the cache.

# Content

- [AWS Account Context](#aws_account_context)
- [Query the Account Context Cache](#aws_account_context_query)
  - [Query-Syntax](#query_syntax)
- [ACAI JSON-Engine](#acai_json_engine)
  - [Basic Expressions](#basic_expressions)
  - [Logical Expressions](#logical_expressions)
  - [Pattern JSON Examples](#acai_json_engine_examples)
- [Cache-Query Examples](#cache_query_examples)



## AWS Account Context <a id="aws_account_context"></a> [🔝](#top)

Each AWS account context includes information like account-ID, account-name, account-tags, and Organizational Unit (OU) details.
In JSON (JavaScript Object Notation) format the 

```python
account_context = {
    "accountId": "905418151472",
    "accountName": "acai_aws-lab1_wl2",
    "accountStatus": "ACTIVE",
    "accountTags": {
        "owner": "Finance",
        "environment": "Non-Prod",
        "application": "SAP",
        "type": "Workload",
        "confidentiality_level": "Restricted"
    },
    "ouId": "ou-er26-hsal28aq",
    "ouIdWithPath": "o-3iuv4h36uk/r-er26/ou-er26-08tbwblz/ou-er26-sgxk358u/ou-er26-hsal28aq",
    "ouName": "NonProd",
    "ouNameWithPath": "Root/Lab_WorkloadAccounts/BusinessUnit_1/NonProd",
    "ouTags": {
        "module_provider": "ACAI GmbH",
        "environment": "Production",
        "module_source": "github.com/acai-consulting/terraform-aws-acf-org-ou-mgmt",
        "application": "AWS MA Core",
        "cicd_ado_organization": "acai-consulting",
        "cicd_branch_name": "initial_version",
        "cicd_pipeline_name": "Org-Mgmt",
        "module_name": "terraform-aws-acf-org-ou-mgmt",
        "module_version": "1.1.1",
        "cicd_ado_project_name": "aws-lab-2024"
    }
  "accountId": "905418151471",
  "accountName": "acai_aws-lab1_wl2",
  "accountStatus": "ACTIVE",
  "accountTags": {
    "owner": "Finance",
    "environment": "Non-Prod",
    "application": "SAP",
    "type": "Workload",
    "confidentiality_level": "Restricted"
  },
  "ouId": "ou-er26-hsal28aq",
  "ouIdWithPath": "o-3iuv4h36uk/r-er26/ou-er26-08tbwblz/ou-er26-sgxk358u/ou-er26-hsal28aq",
  "ouName": "NonProd",
  "ouNameWithPath": "Root/Lab_WorkloadAccounts/BusinessUnit_1/NonProd",
  "ouTags": {
    "module_provider": "ACAI GmbH",
    "environment": "Production",
    "module_source": "github.com/acai-consulting/terraform-aws-acf-org-ou-mgmt",
    "application": "AWS MA Core",
    "cicd_ado_organization": "acai-consulting",
    "cicd_branch_name": "initial_version",
    "cicd_pipeline_name": "Org-Mgmt",
    "module_name": "terraform-aws-acf-org-ou-mgmt",
    "module_version": "1.1.1",
    "cicd_ado_project_name": "aws-lab-2024"
  }
}
```

[Full Inventory of ACAI AWS Lab](https://github.com/acai-consulting/acai.public/blob/main/chat-bots/acf-context-query/full_account_cache.json)

## Query the Account Context Cache <a id="aws_account_context_query"></a> [🔝](#top)

In large AWS Orgnizations it is a typical use case to query groups of accounts that have similar common criteria.
To query for a list of accounts the ACF Account Context Cache supports a JSON based query following the format:

### Query-Syntax <a id="query_syntax"></a> [🔝](#top)
To query for a list of accounts the ACF Account Context Cache supports a **Query JSON** following this format:

```text
For all accounts in the cache:
query_json = "*" 

For selected accounts in the cache:
query_json = {
    "exclude": "*" | Pattern JSON-Object | [
        Pattern JSON-Object
    ],
    "forceInclude": Pattern JSON-Object | [
        Pattern JSON-Object
    ]
}

or query_json = [
    {
        "exclude": "*" | Pattern JSON-Object | [
            Pattern JSON-Object
        ],
        "forceInclude": Pattern JSON-Object | [
            Pattern JSON-Object
        ]
    },
    {
        "exclude": "*" | Pattern JSON-Object | [
            Pattern JSON-Object
        ],
        "forceInclude": Pattern JSON-Object | [
            Pattern JSON-Object
        ]
    },
    ...
]
```

| Key           | Value-Type                                                 | Comment    |
| :---          | :---                                                       | :---       |
| .exclude      | "*" or Pattern JSON-Object or List of Pattern JSON-Objects | (optional) |
| .forceInclude | Pattern JSON-Object or List of Pattern JSON-Objects        | (optional) |

![JSON-Query-Image]

##  ACAI JSON-Engine<a id="acai_json_engine"></a> [🔝](#top)

The principle of the ACAI JSON-Engine is based on the comparison of a **Pattern JSON** with a **Source JSON**.

### Basic Expressions <a id="basic_expressions"></a> [🔝](#top)

The syntax of the **Pattern JSON** is in alignment with [Amazon EventBridge > Create event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html#eb-create-pattern):

| Comparison | Example | Rule syntax | Matching source example |
| :---   | :---  | :---  | :---  |
| Equals | Name is "Alice" | "Name": "Alice" or "Name": [ "Alice" ]  | "Name": "Alice" |
| And | Location is "New York" and Day is "Monday" | "Location": "New York", <br/>"Day": "Monday" | "Location": "New York",<br/> "Day": "Monday" |
| Or | PaymentType is "Credit" | "Debit" | "PaymentType": [ "Credit", "Debit"] | "PaymentType": "Credit" |
| Empty | LastName is empty | "LastName": [""] | "LastName": "" |
| "Nesting" | Customer.Name is "Alice" | "Customer": JSON-Object | "Customer": { "Name": "Alice" }  |
| Mix | Location is "New York" and Day is "Monday" or "Tuesday" | "Location": "New York", <br/> "Day": ["Monday", "Thuesday"] | "Location": "New York", "Day": "Monday" or <br/> "Location": "New York", "Day": "Tuesday" |

### Logical Expressions <a id="logical_expressions"></a> [🔝](#top)

Additional **Logical Expressions** are supported. In this case, the JSON-Value is a JSON-Array of JSON-Objects:

```Note
**Note**
For the ACAI JSON-Engine the keys of the Pattern JSON are case-insensitive to the Source JSON. 
```

| Comparison | Comparator | Example | Logical Expression Syntax | Matching Source JSON |
| :---   | :---  |  :---  | :---  | :---  |
| Begins with | prefix | Region is in the US | "Region": [ {"prefix": "us-" } ] | "Region": "us-east-1" |
| Contains | contains | ServiceName contains 'database' | "ServiceName": [ <br/>  {"contains": "database" } <br/>] |  "serviceName": "employee-database-dev" |
| Does not contain | contains-not | ServiceName does not contain 'database' | "ServiceName": [ <br/>  {"contains-not": "database" } <br/>] |  "serviceName": "employee-microservice-dev" |
| Ends with | suffix | Service name ends with "-dev" | "serviceName": [ {"suffix": "-dev" } ] | "ServiceName": "employee-database-dev" |
| Not | anything-but | Weather is anything but "Raining" | "Weather": [<br/>  { "anything-but": "Raining" } <br/>] | "Weather": "Sunny" or "Cloudy" |
| Exists | exists | ProductName exists | "ProductName": [ { "exists": true } ] | "ProductName": "SEMPER" |
| Does not exist | exists | ProductName does not exist | "ProductName": [ { "exists": false } ] | n/a |
| REGEX match | regex-match | ServiceName matches regex pattern "^prefix-\w+-prod$" |  "ServiceName": [<br/>  { "regex-match": "^prefix-\w+-prod$" } <br/>] |  "ServiceName": "prefix-database-prod" |
| REGEX not match | regex-not-match | ServiceName does not match regex pattern "^prefix-\w+-prod$" |  "ServiceName": [<br/>  { "regex-match": "^prefix-\w+-prod$" } <br/>] |  "ServiceName": "prefix-database-int" |

## Pattern JSON Examples <a id="acai_json_engine_examples"></a> [🔝](#top)

### AND Expression [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
{
     "accountTags": {
        "confidentiality_level": "Internal"
    },
    "ouName": "Prod"
}
```

```text
-> Pattern JSON will match to all accounts where account_context.accountTags.confidentiality_level == "Internal" AND account_context.ouName == "Prod".
```

### OR Expression [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
{
     "accountTags": {
        "environment": [
            "prod",
            "nonprod"
        ]
    }
}
```

```text
-> Pattern JSON will match to all accounts where account_context.accountTags.environment == "prod" OR account_context.accountTags.environment == "nonprod".
```

### Logical Expression - Comparator "contains" [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "accountName": [
        {
            "contains": "_core-"
        }
    ]
}
```

```text
-> Pattern JSON will match to all accounts where account_context.accountName will contain "_core-".
```

### Logical Expression - Comparator "exists" [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
{
     "accountTags": {
        "confidantiality_level": [
            {
                "exists": true
            }
        ]
    }
}
```

```text
-> Pattern JSON will match to all accounts where the JSON-Key account_context.accountTags.confidantiality_level is available.
```

### Comparator "regex-*" [🔝](#top)

For regex expressions we recommend: https://www.autoregex.xyz/

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "eventType": [{"regex-match": "^Aws"}]
}
```

```text
-> Pattern JSON will match to the Source JSON as the 
   "eventType": "AwsApiCall" matches the pattern.
```

## Cache-Query Examples <a id="cache_query_examples"></a> [🔝](#top)

### Cache-Query Example #1 [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
query_json = {
    "exclude": "*",
    "forceInclude": {
        "accountTags": {
            "environment": "Non-Prod"
        }
    }
}
```

```text
Selects all AWS Accounts that are not "accountContext"."accountTags"."environment" equals "Non-Prod".
```

### Cache-Query Example #2 [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
query_json =  {
    "exclude": "*",
    "forceInclude": {
        "accountName": [
            {
                "contains": "-core-"
            }
        ]
    }
}
```

```text
Selects all AWS Accounts where "accountContext"."accountName" contains "-core-".
```

### Cache-Query Example #3 [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
query_json = {
    "exclude": "*",
    "forceInclude": [
        {
            "accountTags": {
                "environment": "Non-Prod"
            },
            "ouNameWithPath": [
                {
                    "contains": "BusinessUnit_1"
                }
            ]
        }
    ]
}
```

```text
Selects all AWS Accounts where "accountContext"."accountTags"."environment" equals "nonprod" and "accountContext"."ouNameWithPath" contains "department_a_".
```

### Cache-Query Example #4 [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
query_json = {
    "exclude": "*",
    "forceInclude": [
        {
            "accountTags": {
                "environment": "nonprod"
            }
        },
        {
            "ouNameWithPath": [
                {
                    "contains": "sandbox"
                }
            ]
        }
    ]
}
```

```text
Selects all AWS Accounts where "accountContext"."accountTags"."environment" equals "nonprod" or "accountContext"."ouNameWithPath" contains "sandbox".
```

### Cache-Query Example #5 [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
query_json = [
    {
        "exclude": "*",
        "forceInclude": {
            "ouNameWithPath": [
                {
                    "contains": "dept_2"
                }
            ]
        }
    },
    {
        "exclude": "*",
        "forceInclude": {
            "accountTags": {
                "environment": "prod"
            },
            "ouNameWithPath": [
                {
                    "contains": "dept_1"
                }
            ]
        }
    }
]
```

```text
Selects all AWS Accounts where "accountContext"."ouNameWithPath" contains "dept_2" or where "accountContext"."accountTags"."environment" equals "prod" and "accountContext"."ouNameWithPath" contains "dept_1".
```

<!-- MARKDOWN LINKS & IMAGES -->
[acai-shield]: https://img.shields.io/badge/maintained_by-acai.gmbh-CB224B?style=flat
[acai-url]: https://acai.gmbh
[acai-copyright-shield]: https://img.shields.io/badge/copyright-acai.gmbh-CB224B?style=flat

[JSON-Query-Image]: ./docs/JSON-Query.svg
