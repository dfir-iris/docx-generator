# **Global Functions**

## Add Hyperlink

**`{{r addHyperlink(__link_caption__, __link_url__) }}`**  
**`{{r addHyperlink(__link_caption__, __link_url__, __style_name__) }}`**

Adds a hyperlink to the final document.

The `__style_name__` parameter is optional. There is no default  value.

## Add Image

* **Local**

**`{{p addPicture(key_in_json_data) }}`**  
**`{{p addPicture(key_in_json_data, '__postion__') }}`**

Adds picture to the final document from a local path. This local path must be relative to the base path passed to the `generate_docx` method.

The `addPicture` filter takes as parameter `__postion__` which refers to the position you want the picture to be placed.  
Available values are:  
`'LEFT'`, `'CENTER'`, `'RIGHT'`, `'JUSTIFY'`, `'DISTRIBUTE'`, `'JUSTIFY_MED'`, `'JUSTIFY_HI'`, `'JUSTIFY_LOW'`, `'THAI_JUSTIFY'`  
Default value is `'CENTER'`

* **UUID**

**`{{p addPictureFromUuid(key_in_json_data )}}`**
**`{{p addPictureFromUuid(key_in_json_data, '__postion__') }}`**

Adds picture to the final document from a folder named after a uuid. This uuid folder must be at the root level of the base path.

Same thing as local for `__postion__` parameter. 

## Add Sub Document

* **Local**

**`{{p addSubDocument(key_in_json_data) }}`**

Integrates the content of a locally stored .docx document where the Jinja2 tag is placed.

* **UUID**

**`{{p addSubDocumentFromUuid(key_in_json_data )}}`**

Integrates the content of a .docx document stored in a folder having as name a Uuid, where the Jinja2 tag is placed.

## Other Global Functions

Default Jinja2 global functions are also available.  
You can find them [here](https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-global-functions)
