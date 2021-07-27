#!/usr/bin/env python3

"""Point-of-entry script."""

from collections import OrderedDict
import csv
from itertools import permutations
import os
import re
import sys
import json

from nltk.tokenize import word_tokenize

import lexmapr.pipeline_resources as pipeline_resources
import lexmapr.pipeline_helpers as helpers


def run(args):

    """
    Main text mining pipeline.
    """
    # If the user specified a profile, we must retrieve args specified
    # by the profile, unless they were explicitly overridden.
    if args.profile:
        args = pipeline_resources.get_profile_args(args)

    # To contain resources fetched from online ontologies, if any.
    # Will eventually be added to ``lookup_table``.
    ontology_lookup_table = None
    if args.config:
        # Fetch online ontology terms specified in config file.
        ontology_lookup_table = pipeline_resources.get_config_resources(
            args.config, args.no_cache)
    elif args.profile:
        # Fetch online ontology terms specified in profile.
        ontology_lookup_table = pipeline_resources.get_profile_resources(
            args.profile)

    # Input file
    fr = open(args.input_file, "r")
    _, ext = os.path.splitext(args.input_file)
    if ext == ".csv":
        fr_reader = csv.reader(fr, delimiter=",")
    elif ext == ".tsv":
        fr_reader = csv.reader(fr, delimiter="\t")
    else:
        raise ValueError("Should not reach here")
    # Skip header
    next(fr_reader)

    map_result = {
        "mapping_output": {},
        "input_to_ontology_mapping": {},
        "ontology_to_input_mapping": {},
        "input_term_label": {},
        "ontology_term_label": {}
    }

    for row in fr_reader:
        input_term_id = row[0].strip()
        input_term_label = row[1].strip()
        input_term = "%s:%s" % (input_term_label, input_term_id)
        map_result["mapping_output"][input_term] = ""

    map_result = find_match(map_result, ontology_lookup_table)

    fw = open(args.output, 'w') if args.output else sys.stdout
    fw.write(json.dumps(map_result, indent=3))


def find_match(map_result, ontology_lookup_table):

    mapping_output = map_result["mapping_output"]
    input_to_ontology_mapping = map_result["input_to_ontology_mapping"]
    ontology_to_input_mapping = map_result["ontology_to_input_mapping"]
    input_term_label_map = map_result["input_term_label"]
    ontology_term_label_map = map_result["ontology_term_label"]

    for input_term, mapping_object in mapping_output.items():

        input_term_id = get_term_id(input_term)
        input_term_label = get_term_label(input_term)

        # Standardize sample to lowercase and with punctuation treatment.
        sample = input_term_label.lower()
        sample = helpers.punctuation_treatment(sample)

        # Tokenize sample and remove stop words and 1-letter words
        sample_tokens = word_tokenize(sample)

        # Get "cleaned_sample"
        cleaned_sample = ""
        for token in sample_tokens:
            # Ignore dates
            if helpers.is_date(token) or helpers.is_number(token):
                continue
            # Ignore single letter
            if helpers.is_single_letter(token):
                continue

            # Some preprocessing
            token = helpers.preprocess(token)

            lemma = helpers.singularize_token(
                token, ontology_lookup_table, [])
            lemma = helpers.spelling_correction(
                lemma, ontology_lookup_table, [])
            lemma = helpers.abbreviation_normalization_token(
                lemma, ontology_lookup_table, [])
            lemma = helpers.non_English_normalization_token(
                lemma, ontology_lookup_table, [])

            cleaned_sample = helpers.get_cleaned_sample(
                cleaned_sample, lemma, ontology_lookup_table)
            cleaned_sample = re.sub(' +', ' ', cleaned_sample)
            cleaned_sample = helpers.abbreviation_normalization_phrase(
                cleaned_sample, ontology_lookup_table, [])
            cleaned_sample = helpers.non_English_normalization_phrase(
                cleaned_sample, ontology_lookup_table, [])

        cleaned_sample = helpers.remove_duplicate_tokens(cleaned_sample)

        # Attempt full term match
        full_term_match = helpers.map_term(sample, ontology_lookup_table)

        if not full_term_match:
            # Attempt full term match with cleaned sample
            full_term_match =\
                helpers.map_term(cleaned_sample,
                                 ontology_lookup_table)
        if not full_term_match:
            # Attempt full term match using suffixes
            full_term_match =\
                helpers.map_term(sample,
                                 ontology_lookup_table,
                                 consider_suffixes=True)
        if not full_term_match:
            # Attempt full term match with cleaned sample using suffixes
            full_term_match =\
                helpers.map_term(cleaned_sample,
                                 ontology_lookup_table,
                                 consider_suffixes=True)

        if full_term_match:
            ontology_term_id = full_term_match["id"].upper()
            ontology_term_label = full_term_match["term"]
            ontology_term = "%s:%s" % (ontology_term_label, ontology_term_id)
            mapping_output[input_term] = ontology_term
            input_to_ontology_mapping[input_term_id] = ontology_term_id
            ontology_to_input_mapping[ontology_term_id] = input_term_id
            ontology_term_label_map[ontology_term_id] = full_term_match["term"]
            input_term_label_map[input_term_id] = input_term_label
        else:
            # Attempt various component matches
            component_matches = []
            covered_tokens = set()

            for i in range(5, 0, -1):
                for gram_chunk in helpers.get_gram_chunks(cleaned_sample, i):
                    concat_gram_chunk = " ".join(gram_chunk)
                    gram_tokens = word_tokenize(concat_gram_chunk)
                    gram_permutations =\
                        list(OrderedDict.fromkeys(permutations(
                            concat_gram_chunk.split())))

                    # gram_tokens covered in prior component match
                    if set(gram_tokens) <= covered_tokens:
                        continue

                    for gram_permutation in gram_permutations:
                        gram_permutation_str = " ".join(gram_permutation)
                        component_match =\
                            helpers.map_term(gram_permutation_str,
                                             ontology_lookup_table)
                        if not component_match:
                            # Try again with suffixes
                            component_match =\
                                helpers.map_term(gram_permutation_str,
                                                 ontology_lookup_table,
                                                 consider_suffixes=True)
                        if component_match:
                            component_matches.append(component_match)
                            covered_tokens.update(gram_tokens)
                            break

            # We need should not consider component matches that are
            # ancestral to other component matches.
            ancestors = set()
            for component_match in component_matches:
                component_match_hierarchies =\
                    helpers.get_term_parent_hierarchies(component_match["id"],
                                                        ontology_lookup_table)

                for component_match_hierarchy in component_match_hierarchies:
                    # We do not need the first element
                    component_match_hierarchy.pop(0)

                    ancestors |= set(component_match_hierarchy)

            matched_components = []
            for component_match in component_matches:
                if component_match["id"] not in ancestors:
                    matched_component =\
                        "%s:%s" % (component_match["term"],
                                   component_match["id"])
                    matched_components.append(matched_component)

            # TODO: revisit this step.
            # We do need it, but perhaps the function could be
            #  simplified?
            if len(matched_components):
                matched_components = helpers.retain_phrase(matched_components)

            if matched_components:
                if len(matched_components) == 1:
                    single_value = matched_components[0]
                    onto_term_id = get_term_id(single_value)
                    onto_term_label = get_term_label(single_value)
                    mapping_output[input_term] = single_value
                    input_to_ontology_mapping[input_term_id] = onto_term_id
                    if onto_term_id not in ontology_to_input_mapping:
                        ontology_to_input_mapping[onto_term_id] = input_term_id
                    ontology_term_label_map[onto_term_id] = onto_term_label
                    input_term_label_map[input_term_id] = input_term_label
                else:
                    mapping_output[input_term] = matched_components
                    input_to_ontology_mapping[input_term_id] =\
                        [onto_term_id for onto_term_id in map(
                            lambda s: get_term_id(s), matched_components)]
                    input_term_label_map[input_term_id] = input_term_label
                    for ontology_term in matched_components:
                        onto_term_id = get_term_id(ontology_term)
                        onto_term_label = get_term_label(ontology_term)
                        ontology_term_label_map[onto_term_id] = onto_term_label

    return map_result


def get_term_id(string_term):
    return string_term.split(":")[1].upper()


def get_term_label(string_term):
    return string_term.split(":")[0]
