"""
Example Usage: 

python scripts/compare_models_on_dataset.py data/analysis_results/glue_mrpc_1+2_distilgpt2.h5 data/analysis_results/glue_mrpc_1+2_gpt2.h5 -o data/compared_results --bidirectional
"""

import argparse
from analysis.analysis_results_dataset import H5AnalysisResultDataset
from typing import *
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from analysis import LMAnalysisOutputH5, H5AnalysisResultDataset
from tqdm import tqdm
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument(
    "ds1",
    type=str,
    help="path to first H5AnalysisResultDataset",
)
parser.add_argument(
    "ds2",
    type=str,
    help="path to second h5 file",
)
parser.add_argument(
    "--output_dir",
    "-o",
    type=str,
    default=None,
    help="Which directory to store the output h5 file with the default name.",
)
parser.add_argument(
    "--max_clamp_rank",
    type=int,
    default=50,
    help="Ranks beyond this are clamped to this value",
)
parser.add_argument(
    "--bidirectional",
    action="store_true",
    help="If passed, compute an ds1 -> ds2 evaluation in addition to an ds2 -> ds1 evaluation. Some of the 'metrics' are asymmetric",
)

args = parser.parse_args()


def ex_compare(ex1: LMAnalysisOutputH5, ex2: LMAnalysisOutputH5, max_rank=50):
    r1 = ex1.ranks.astype(np.int32)
    r2 = ex2.ranks.astype(np.int32)
    clamped_r1 = np.clip(r1, 0, max_rank)
    clamped_r2 = np.clip(r2, 0, max_rank)
    p1 = ex1.probs
    p2 = ex2.probs

    rank_diff = r2 - r1
    prob_diff = p2 - p1
    clamped_rank_diff = clamped_r2 - clamped_r1
    kl_diff = F.kl_div(torch.tensor(p1), torch.tensor(p2), reduction="sum")

    topk_token_set1 = [set(t) for t in ex1.topk_token_ids]
    topk_token_set2 = [set(t) for t in ex2.topk_token_ids]
    n_topk_diff = np.array([len(s1.difference(s2)) for s1, s2 in zip(topk_token_set1, topk_token_set2)])

    return {
        "n_tokens": len(r1),
        "avg_rank_diff": np.mean(rank_diff),
        "max_rank_diff": np.max(rank_diff),
        "avg_clamped_rank_diff": np.mean(clamped_rank_diff),
        "max_clamped_rank_diff": np.max(clamped_rank_diff),
        "avg_prob_diff": np.mean(prob_diff),
        "max_prob_diff": np.max(prob_diff),
        "kl": kl_diff.item(),
        "avg_topk_diff": n_topk_diff.mean(),
        "max_topk_diff": n_topk_diff.max()
    }

if args.output_dir is None: output_dir = Path(".")
else: output_dir = Path(args.output_dir)
if output_dir.is_file(): raise ValueError("Specified output dir cannot be an existing file")
output_dir.mkdir(parents=True, exist_ok=True)

# Smart defaults
def compare_datasets(ds1_name, ds2_name):
    ds1 = H5AnalysisResultDataset.from_file(ds1_name)
    ds2 = H5AnalysisResultDataset.from_file(ds2_name)


    assert ds1.dataset_name == ds2.dataset_name, "The two datasets should have the same name"
    ds_name = ds1.dataset_name
    assert ds1.dataset_checksum == ds2.dataset_checksum, "The two datasets should have the same checksum of contents"

    # Below is BROKEN because python's `hash` function changes between process runs
    # assert ds1.vocab_hash == ds2.vocab_hash, "The two datasets should be created by models that share the same vocabulary"

    default_name = f"{ds1.model_name}_{ds2.model_name}_{ds_name}.csv"
    output_f = output_dir / default_name

    diff_ab = [ex_compare(exa, exb, max_rank=args.max_clamp_rank)for exa, exb in tqdm(zip(ds1, ds2), total=len(ds1))]
    df = pd.DataFrame(data=diff_ab)
    print(f"     Saving analysis results to {output_f}")
    df.to_csv(output_f)

compare_datasets(args.ds1, args.ds2)
if args.bidirectional:
    print("\n\nRepeating with inverted datasets\n\n")
    compare_datasets(args.ds2, args.ds1)