# Copyright (c) 2023 Valentin Knappich and Timo Schrader
#
# This source code is licensed under the MIT license (https://opensource.org/license/mit/)

import json
import logging
import os.path
import random
from argparse import ArgumentParser
from pathlib import Path

import numpy as np
import spacy
import tqdm

logging.getLogger().setLevel(logging.INFO)
project_root = Path(__file__).absolute().parent.parent.parent.parent

parser: ArgumentParser = ArgumentParser()

parser.add_argument(
    "--input_path",
    type=str,
    help="Path to input dataset files",
    default=str(project_root / "data/webnlg_2017"),
)
parser.add_argument(
    "--output_path",
    type=str,
    help="Path for storing created dataset files",
    default=str(project_root / "data/webnlg_active_passive_subset"),
)
parser.add_argument("--train_size", type=int, help="Amount of training samples", default=99999)
parser.add_argument("--dev_size", type=int, help="Amount of training samples", default=99999)
parser.add_argument("--test_size", type=int, help="Amount of training samples", default=99999)
parser.add_argument("--seed", type=int, help="Seed for random generator", default=1337)
parser.add_argument(
    "--type",
    type=str,
    choices=["distinct", "mixed"],
    help="""Whether to create distict AP samples or mixed samples.
            Mixed samples are required for contrastive learning.""",
    default="distinct",
)

args = parser.parse_args()

# Spacy dependency parser tags which strongly indicate passive sentences
PASSIVE_VOICE_INDICATORS: list = ["nsubjpass", "agent", "auxpass"]


class PassiveVoiceDetector:
    def __init__(self, model="en_core_web_trf") -> None:
        try:
            self.model = spacy.load(model)
        except OSError:
            from spacy.cli import download

            download("en_core_web_lg")
            self.model = spacy.load(model)

    def check_sentences_for_passive_voice(self, input_sentences: list) -> np.ndarray:
        result: list[bool] = [False] * len(input_sentences)
        assert input_sentences is not None, "Input list must not be None."
        for i, sent in enumerate(input_sentences):
            sent_doc: spacy.tokens.doc.Doc = self.model(sent)
            tokens: list = list(sent_doc)
            for t in tokens:
                if t.dep_ in PASSIVE_VOICE_INDICATORS:
                    result[i] = True
                    break
        return np.array(result, dtype=bool)

    def is_sentence_passive(self, input_sentence: str) -> bool:
        assert input_sentence is not None, "Input sentence must not be None."
        sent_doc: spacy.tokens.doc.Doc = self.model(input_sentence)
        tokens: list = list(sent_doc)
        for t in tokens:
            if t.dep_ in PASSIVE_VOICE_INDICATORS:
                return True

        return False


def process_entry(params):
    entry, idx = params
    entry: dict = entry[str(idx + 1)]
    entry["originalIdx"] = str(idx + 1)
    results: list = []

    if args.type == "distinct":

        for lexicalisation in entry["lexicalisations"]:
            entry_: dict = {**entry}  # copy dict
            entry_["lexicalisations"] = [lexicalisation]
            is_passive_list = [
                passive_voice_detector.is_sentence_passive(str(sent))
                for sent in spacy_nlp(lexicalisation["lex"]).sents
            ]
            is_passive = all(is_passive_list)
            is_active = all([not b for b in is_passive_list])

            if is_passive:
                entry_["is_passive"] = 1
            elif is_active:
                entry_["is_passive"] = 0
            else:
                continue  # Dont use mixture of active and passive

            results.append(entry_)

    elif args.type == "mixed":
        entry_: dict = {**entry}
        entry_["passive_lexicalisations"] = []
        entry_["active_lexicalisations"] = []

        for lexicalisation in entry["lexicalisations"]:
            is_passive_list = [
                passive_voice_detector.is_sentence_passive(str(sent))
                for sent in spacy_nlp(lexicalisation["lex"]).sents
            ]
            is_passive = all(is_passive_list)
            is_active = all([not b for b in is_passive_list])

            if is_passive:
                entry_["passive_lexicalisations"].append(lexicalisation)
            elif is_active:
                entry_["active_lexicalisations"].append(lexicalisation)
            else:
                continue  # Dont use mixture of active and passive

        if (
            len(entry_["passive_lexicalisations"]) > 0
            and len(entry_["active_lexicalisations"]) > 0
        ):
            results.append(entry_)

    return results


output_files: list = ["train.json", "dev.json", "test.json"]
split_sizes: list = [args.train_size, args.dev_size, args.test_size]
random.seed(args.seed)

passive_voice_detector = PassiveVoiceDetector("en_core_web_lg")
spacy_nlp = spacy.load("en_core_web_lg")

for of, split_size in zip(output_files, split_sizes):
    assert not os.path.exists(
        os.path.join(args.output_path, of)
    ), "Path already contains files. Files won't be overridden."

    output_dataset: dict = {"entries": []}
    counters = {"a": 0, "p": 0}

    with open(os.path.join(args.input_path, of), mode="r", encoding="utf-8") as f:
        dataset: dict = json.load(f)

    total_lexs = sum(
        [len(list(entry.values())[0]["lexicalisations"]) for entry in dataset["entries"]]
    )

    with tqdm.tqdm(total=min(split_size, total_lexs), desc=of) as progress:
        result_list: list = []
        for idx, entry in enumerate(dataset["entries"]):
            res = process_entry((entry, idx))
            if len(res) > 0:
                result_list.extend(res)

        for j, result in enumerate(result_list):
            if args.type == "distinct":
                if counters["a"] >= split_size / 2 and counters["p"] >= split_size / 2:
                    break  # When final size is reached
                ap = "p" if result["is_passive"] else "a"
                if counters[ap] < split_size / 2:
                    output_dataset["entries"].append(
                        {str(counters["a"] + counters["p"] + 1): result}
                    )
                    progress.update(1)
                    counters[ap] += 1
            elif args.type == "mixed":
                output_dataset["entries"].append({str(j + 1): result})
                progress.update(1)

                if j == len(result_list) - 1:
                    break
        else:
            # Entered if break was not called
            # For the case that you want as many examples as possible
            smaller_class, larger_class = (
                ("a", "p") if counters["a"] < counters["p"] else ("p", "a")
            )
            to_remove = counters[larger_class] - counters[smaller_class]

            for i in reversed(range(1, len(output_dataset["entries"]) + 1)):
                if not to_remove:
                    break
                # remove examples from the class with too many examples
                example_flag = (
                    "p" if output_dataset["entries"][i - 1][str(i)]["is_passive"] else "a"
                )
                if example_flag == larger_class:
                    output_dataset["entries"].pop(i - 1)
                    to_remove -= 1

            # Reset indices after removing
            ids = range(1, len(output_dataset["entries"]) + 1)
            output_dataset["entries"] = [
                {id: list(data.values())[0]} for id, data in zip(ids, output_dataset["entries"])
            ]

    if len(output_dataset["entries"]) < split_size:
        logging.warning(
            f"Requested number of samples {split_size} not available. "
            f"Got {len(output_dataset['entries'])}"
        )
    if not os.path.exists(os.path.join(args.output_path)):
        os.makedirs(os.path.join(args.output_path), exist_ok=False)
    with open(os.path.join(args.output_path, of), mode="w", encoding="utf-8") as f:
        json.dump(output_dataset, f, indent=3)
