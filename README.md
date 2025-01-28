# Parametrized Cylc Workflow

## Introduction

This library has been created with the goal to provide a general interface to use Cylc inside a more complex python framework.

## Requirements

### Install cylc via conda

```shell
conda create -n cylc --file spec_cylc.txt
```


## Usage

### Create an istance

```shell
from src.cylc import CylcEngine

cylc_engine = CylcEngine("wf/flow.cylc")
