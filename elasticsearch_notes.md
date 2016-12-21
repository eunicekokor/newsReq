#To view all values available mappings in elasticsearch

`GET /_all/_mapping`

#Command to map articles in elasticsearch
```
PUT news
{
   "mappings": {
      "article": {
          "properties": {
              "id":{
                  "type": "string"
              },
              "body":{
                  "type": "string"
              },
              "author":{
                  "type": "string"
              },
              "source":{
                  "type": "string"
              },
              "category":{
                  "type": "string"
              }
          }
      }
   }
}
```
