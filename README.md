# FoodMapr

This is a derived work from [LexMapr](https://genepio.org/lexmapr/) that focuses on food items and products.

What are the differences:
 * Include the English stop words as the default.
 * Remove the functionalities to output the text buckets and classifications.
 * Remove the micro and macro match statuses.
 * Introduce a new profile called "anz" to map the [Australia New Zealand Food Standards](https://www.foodstandards.gov.au/code/Pages/default.aspx)

## Installation

1. Install [Conda](https://docs.conda.io/en/latest/miniconda.html).

2. Create a FoodMapr environment:

```
$ conda create --name FoodMapr
```

3. Install FoodMapr into your conda environment:
```
$ conda activate FoodMapr
$ git clone https://github.com/johardi/FoodMapr.git
$ cd FoodMapr
$ pip install .
$ python -m nltk.downloader all
```

## Usage

1. Prepare the input file: `food.csv`
```
FoodId,FoodName
F001,Chicken Breast
F002,Baked Potato
F003,Canned Corn
F004,Frozen Yogurt
F005,Apple Pie
```

2. Prepare the configuration file: `config_foodon.json`
```javascript
[
   { "http://purl.obolibrary.org/obo/foodon.owl": [
         "http://purl.obolibrary.org/obo/FOODON_00001871",
         "http://purl.obolibrary.org/obo/FOODON_00002373",
         "http://purl.obolibrary.org/obo/FOODON_00002381",
         "http://purl.obolibrary.org/obo/FOODON_00002645",
         "http://purl.obolibrary.org/obo/FOODON_00001180",
         "http://purl.obolibrary.org/obo/FOODON_03311737",
         "http://purl.obolibrary.org/obo/FOODON_00001714"
      ]
   }
]
```

3. Run the command on the Terminal console

```console
(FoodMapr) foo@bar:~$ foodmapr food.csv -c config_foodon.json
{
   "mapping_output": {
      "Chicken Breast:F001": "chicken breast:FOODON_00002703",
      "Baked Potato:F002": "potato (whole, baked):FOODON_03302196",
      "Canned Corn:F003": "corn (canned):FOODON_03302665",
      "Frozen Yogurt:F004": "frozen yogurt:FOODON_03307445",
      "Apple Pie:F005": "apple pie:FOODON_00002475"
   },
   "input_to_ontology_mapping": {
      "F001": "FOODON_00002703",
      "F002": "FOODON_03302196",
      "F003": "FOODON_03302665",
      "F004": "FOODON_03307445",
      "F005": "FOODON_00002475"
   },
   "ontology_to_input_mapping": {
      "FOODON_00002703": "F001",
      "FOODON_03302196": "F002",
      "FOODON_03302665": "F003",
      "FOODON_03307445": "F004",
      "FOODON_00002475": "F005"
   },
   "input_term_label": {
      "F001": "Chicken Breast",
      "F002": "Baked Potato",
      "F003": "Canned Corn",
      "F004": "Frozen Yogurt",
      "F005": "Apple Pie"
   },
   "ontology_term_label": {
      "FOODON_00002703": "chicken breast",
      "FOODON_03302196": "potato (whole, baked)",
      "FOODON_03302665": "corn (canned)",
      "FOODON_03307445": "frozen yogurt",
      "FOODON_00002475": "apple pie"
   }
}
```

## More Documentation from LexMapr

[Formal documentation](https://genepio.org/lexmapr-documentation/)

[Tutorial slides](./docs/tutorial_slides.pdf) for users with little or no experience with command line

[Tutorial slides](./docs/ifsac_tutorial_slides.pdf) for **IFSAC users** with little or no experience with command line
