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
- [Short JSON Intro](#json_intro)
- [ACAI JSON-Engine](#acai_json_engine)
  - [Syntax Examples](#acai_json_engine_examples)
    - [Source JSON](#acai_json_engine_examples_source)
    - [Pattern JSON](#acai_json_engine_examples_patterns)
      - [AND / OR](#acai_json_engine_examples_and_or)
      - [Comparator "exists"](#acai_json_engine_examples_exists)
      - [Comparator "regex-*"](#acai_json_engine_examples_regex)

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
}
```

[Full Inventory of ACAI AWS Lab](https://github.com/acai-consulting/acai.public/blob/main/chat-bots/acf-context-query/full_account_cache.json)

## Query the Account Context Cache <a id="aws_account_context_query"></a> [🔝](#top)

In large AWS Orgnizations it is a typical use case to query groups of accounts that have similar common criteria.
To query for a list of accounts the ACF Account Context Cache supports a JSON based query following the format:

Syntax

```python
from acai.cache.context_cache import ContextCache
from acai.cache_query.context_cache_query import ContextCacheQuery
# initialze LOGGER

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    context_cache = ContextCache(
        logger=LOGGER, 
        org_reader_role_arn=ORG_READER_ROLE_ARN, 
        context_cache_table_name=CONTEXT_CACHE_TABLE_NAME, 
    ) 

    # For all accounts in the cache:
    context_cache_query = ContextCacheQuery(LOGGER, context_cache)
    query_all = {
        "query": "all"
    }
    result_all = context_cache_query.query_cache(query)
    
    # For selected accounts in the cache:
    query_json = {
        "exclude": "*" | Pattern JSON-Object | [
            Pattern JSON-Object
        ],
        "forceInclude": Pattern JSON-Object | [
            Pattern JSON-Object
        ]
    }
    result_all = context_cache_query.query_cache(query)
```



Pattern JSON-Object = 


### Query-Syntax

```python
    # For all accounts in the cache:
    query_all = {
        "query": "all"
    }
    
    # For selected accounts in the cache:
    query_json = {
        "exclude": "*" | Pattern JSON-Object | [
            Pattern JSON-Object
        ],
        "forceInclude": Pattern JSON-Object | [
            Pattern JSON-Object
        ]
    }
```

| Key           | Value-Type                                                 | Comment    |
| :---          | :---                                                       | :---       |
| .exclude      | "*" or Pattern JSON-Object or List of Pattern JSON-Objects | (optional) |
| .forceInclude | Pattern JSON-Object or List of Pattern JSON-Objects        | (optional) |












**Cache-Query Example #1**

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

**Cache-Query Example #2**

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

**Cache-Query Example #3**

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

**Cache-Query Example #4**

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

**Cache-Query Example #5**

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

# Short JSON Intro <a id="json_intro"></a> [🔝](#top)

A JSON-Object can be seen as a key-value store, able to describe complex models.
The following diagram gives an overview of the most important JSON terms inspired by [www.json.org](https://www.json.org/json-en.html).

# ACAI JSON-Engine <a id="acai_json_engine"></a> [🔝](#top)

The principle of the ACAI JSON-Engine is based on the comparison of a **Pattern JSON** with a **Source JSON**.

The syntax of the **Pattern JSON** is in alignment with [Amazon EventBridge > Create event patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html#eb-create-pattern):

| Comparison | Example | Rule syntax | Matching source example |
| :---   | :---  | :---  | :---  |
| Equals | Name is "Alice" | "Name": "Alice" or "Name": [ "Alice" ]  | "Name": "Alice" |
| And | Location is "New York" and Day is "Monday" | "Location": "New York", <br/>"Day": "Monday" | "Location": "New York",<br/> "Day": "Monday" |
| Or | PaymentType is "Credit" | "Debit" | "PaymentType": [ "Credit", "Debit"] | "PaymentType": "Credit" |
| Empty | LastName is empty | "LastName": [""] | "LastName": "" |
| "Nesting" | Customer.Name is "Alice" | "Customer": JSON-Object | "Customer": { "Name": "Alice" }  |
| Mix | Location is "New York" and Day is "Monday" or "Tuesday" | "Location": "New York", <br/> "Day": ["Monday", "Thuesday"] | "Location": "New York", "Day": "Monday" or <br/> "Location": "New York", "Day": "Tuesday" |

## Logical Expressions <a id="acai_json_engine_logical_expressions"></a> [🔝](#top)

Additional **Logical Expressions** are supported. In this case, the JSON-Value is a JSON-Array of JSON-Objects:

<img src="docs/Logical-Expression.svg" alt="drawing" width="400"/>

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

## Syntax Examples <a id="acai_json_engine_examples"></a> [🔝](#top)

### Source JSON  <a id="acai_json_engine_examples_source"></a> [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "sourceIPAddress": "87.200.73.179",
    "requestParameters": {
        "ipPermissions": {
            "items": [
                {
                    "ipProtocol": "tcp",
                    "fromPort": 70,
                    "toPort": 90,
                    "ipRanges": {
                        "items": [
                            {
                                "cidrIp": "0.0.0.0/16"
                            }
                        ]
                    }
                }
            ]
        }
    },

}
```

### Pattern JSON <a id="acai_json_engine_examples_patterns"></a> [🔝](#top)

#### AND / OR <a id="acai_json_engine_examples_and_or"></a> [🔝](#top)

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "readOnly": false,
    "eventType": "AwsApiCall",
    "recipientAccountId": [
        "123456789012",
        "234567890123"
    ],
    "requestParameters": {
        "ipPermissions": {
            "items": {
                "ipProtocol": "tcp"
            }
        }
    }
}
```

```text
-> Pattern JSON will match to the Source JSON as all conditions are met.
```

#### Comparator "exists" <a id="acai_json_engine_examples_exists"></a> [🔝](#top)

This example will prevent a race-condition for events generated by the auto-remediation principal.

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "userIdentity": {
        "sessionContext": {
            "sessionIssuer": {
                "userName" : [
                    {
                        "exists": false
                    },
                    {
                        "exists": true,
                        "anything-but": "foundation-auto-remediation-role"
                    }      
                ]
            }
        }
    }
}
```

```text
-> Pattern JSON will match to the Source JSON as 
   "userIdentity"."sessionContext"."sessionIssuer"."userName" does not exist in the Source JSON.
   If the node ..."userName" would exist the Pattern JSON would match if 
   the ..."userName" would not be "foundation-auto-remediation-role". 
```


#### Comparator "regex-*" <a id="acai_json_engine_examples_regex"></a> [🔝](#top)

For regex expressions we recommend: https://www.autoregex.xyz/

**"regex-match" Example #1**

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "eventType": [{"regex-match": "^Aws"}]
}
```

```text
-> Pattern JSON will match to the Source JSON as the 
   "eventType": "AwsApiCall" matches the pattern.
```

**"regex-match" Example #2**

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "eventType": [{"regex-match": "^Azure"}]
}
```

```text
-> Pattern JSON will not match to the Source JSON as the 
   "eventType": "AwsApiCall" does not match the pattern.
```

**"regex-not-match" Example #1**

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "eventType": [{"regex-not-match": "^Aws"}]
}
```

```text
-> Pattern JSON will not match to the Source JSON as the 
   "eventType": "AwsApiCall" matches the pattern.
```

**"regex-not-match" Example #2**

```json {linenos=table,hl_lines=[],linenostart=50}
{
    "eventType": [{"regex-not-match": "^Azure"}]
}
```

```text
-> Pattern JSON will match to the Source JSON as the 
   "eventType": "AwsApiCall" does not match the pattern.
```


<!-- MARKDOWN LINKS & IMAGES -->
[acai-shield]: https://img.shields.io/badge/maintained_by-acai.gmbh-CB224B?style=flat
[acai-url]: https://acai.gmbh
[acai-copyright-shield]: https://img.shields.io/badge/copyright-acai.gmbh-CB224B?style=flat

[JSON-Query-Image]: ./docs/JSON-Query.svg
[JSON-Basics-Image]: ./docs/JSON-Basics.svg
[JSON-Engine-Image]: ./docs/JSON-Engine.svg
[JSON-Engine-Scope-Pattern-Image]: ./docs/JSON-Engine-Scope-Pattern.svg
