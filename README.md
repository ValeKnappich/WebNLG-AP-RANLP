# WebNLG-AP-RANLP

This is the official repository for *"Controllable Active-Passive Voice Generation using Prefix Tuning"* presented at SWE@RANLP2023.

This research project was fully conducted at the [IMS Stuttgart](https://www.ims.uni-stuttgart.de/) in summer 2022 as part of graduate studies. No other affiliation was included in any way in this project.

Cite this work as 

```bibtex
@inproceedings{knappich-schrader-2023-controllable,
    title = "Controllable Active-Passive Voice Generation using Prefix Tuning",
    author = "Knappich, Valentin  and
      Schrader, Timo Pierre",
    editor = "Hardalov, Momchil  and
      Kancheva, Zara  and
      Velichkov, Boris  and
      Nikolova-Koleva, Ivelina  and
      Slavcheva, Milena",
    booktitle = "Proceedings of the 8th Student Research Workshop associated with the International Conference Recent Advances in Natural Language Processing",
    month = sep,
    year = "2023",
    address = "Varna, Bulgaria",
    publisher = "INCOMA Ltd., Shoumen, Bulgaria",
    url = "https://aclanthology.org/2023.ranlp-stud.3",
    pages = "23--32",
}

```

We base our work on the dataset WebNLG introduces by Gardent et al. 2017.

Claire Gardent, Anastasia Shimorina, Shashi Narayan, and Laura Perez-Beltrachini. 2017. Creating training corpora for NLG micro-planners. In *Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics*, ACL 2017, *Vancouver, Canada, July 30 - August 4, Volume 1: Long Papers*, pages 179–188. Association for Computational Linguistics.

## Dataset Creation Script

We provide the script that creates the AP subsets based on the original WebNLG datset. We build upon the WebNLG version of the [thunlp/OpenPrompt](https://github.com/thunlp/OpenPrompt) repository. Please use this version to fully reproduce the results of the paper. Alternatively, you can also use any other version of WebNLG that sticks to the same data format.

Please create your Python environment from [environment.yml](environment.yml) to run the script.

To run the WebNLG-AP and WebNLG-AP-Pairs pipeline, execute `python create_active_passive_dataset.py <ARGS>`. The following arguments can be set:
- `--input_path`: Path to the WebNLG dataset
- `--output_path`: Path to store the AP subsets
- `--train_size`: Number of train samples to generate
- `--dev_size`: Number of dev samples to generate
- `--test_size`: Number of test samples to generate
- `--seed`: Keep as is
- `--type`: Sets whether distinct active and passive samples, i.e., only one voice per instance or mixed samples, i.e., both voices per instance should be generated. Mixed samples are required for the contrastive learning approach and result in the WebNLG-AP-Pairs dataset.

## WebNLG-AP

This dataset is a subset of the WebNLG dataset with voice annotations. We refer to the paper for details regarding the dataset creations.
See the json structure below. 

```json
{
   "entries": [
      {
         "1": {
            "category": "Airport",
            "dbpedialinks": [],
            "lexicalisations": [
               {
                  "comment": "good",
                  "lang": "",
                  "lex": "The leader of Aarhus is Jacob Bundsgaard.",
                  "xml_id": "Id1"
               }
            ],
            "links": [],
            "modifiedtripleset": [
               {
                  "object": "Jacob_Bundsgaard",
                  "property": "leaderName",
                  "subject": "Aarhus"
               }
            ],
            "originaltriplesets": {
               "originaltripleset": [
                  [
                     {
                        "object": "Jacob_Bundsgaard",
                        "property": "leaderName",
                        "subject": "Aarhus"
                     }
                  ]
               ]
            },
            "shape": "NA",
            "shape_type": "NA",
            "size": "1",
            "xml_id": "Id1",
            "originalIdx": "1",
            "is_passive": 0
         }
      }
   ]
}
```

## WebNLG-AP-Pairs

This is a subset of WebNLG-AP, with exactly one passive and one active lexicalisation per tripleset. We refer to the paper for details regarding the dataset creations.
See the json structure below. Note the "is_passive" flag, where 0 means active voice and 1 means passive voice.

```json
{
   "entries": [
      {
         "1": {
            "category": "Airport",
            "dbpedialinks": [],
            "lexicalisations": [
               {
                  "comment": "good",
                  "lang": "",
                  "lex": "Adolfo Su\u00e1rez Madrid\u2013Barajas Airport is found in San Sebasti\u00e1n de los Reyes.",
                  "xml_id": "Id1"
               },
               {
                  "comment": "good",
                  "lang": "",
                  "lex": "Adolfo Suarez Madrid- Barajas airport is located at San Sebastian de los Reyes.",
                  "xml_id": "Id2"
               },
               {
                  "comment": "good",
                  "lang": "",
                  "lex": "The Adolfo Su\u00e1rez Madrid\u2013Barajas Airport is in San Sebasti\u00e1n de los Reyes.",
                  "xml_id": "Id3"
               }
            ],
            "links": [],
            "modifiedtripleset": [
               {
                  "object": "San_Sebasti\u00e1n_de_los_Reyes",
                  "property": "location",
                  "subject": "Adolfo_Su\u00e1rez_Madrid\u2013Barajas_Airport"
               }
            ],
            "originaltriplesets": {
               "originaltripleset": [
                  [
                     {
                        "object": "San_Sebasti\u00e1n_de_los_Reyes",
                        "property": "location",
                        "subject": "Adolfo_Su\u00e1rez_Madrid\u2013Barajas_Airport"
                     }
                  ]
               ]
            },
            "shape": "NA",
            "shape_type": "NA",
            "size": "1",
            "xml_id": "Id5",
            "originalIdx": "5",
            "passive_lexicalisations": [
               {
                  "comment": "good",
                  "lang": "",
                  "lex": "Adolfo Su\u00e1rez Madrid\u2013Barajas Airport is found in San Sebasti\u00e1n de los Reyes.",
                  "xml_id": "Id1"
               }
            ],
            "active_lexicalisations": [
               {
                  "comment": "good",
                  "lang": "",
                  "lex": "The Adolfo Su\u00e1rez Madrid\u2013Barajas Airport is in San Sebasti\u00e1n de los Reyes.",
                  "xml_id": "Id3"
               }
            ]
         }
      }
  ]
}
```

## License
The script is licensed under the [MIT license](https://opensource.org/license/mit/). The WebNLG dataset is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt).