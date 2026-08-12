# R Demo Plugin

This plugin demonstrates how to build a polyglot tool in Jarvis using R. It uses the `subprocess` runtime to execute an R script (`run.R`) that reads JSON from `stdin` and writes JSON to `stdout`.

## Prerequisites

To use this plugin, you must have R installed on the host machine where the Jarvis backend runs.

### 1. Install R

- **Windows**: Download and install from [CRAN](https://cran.r-project.org/bin/windows/base/). Ensure `Rscript` is added to your system `PATH`.
- **macOS**: `brew install r`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install r-base`

### 2. Install Required R Packages

The script uses the `jsonlite` package for JSON I/O. Install it by running the following command in your terminal or R console:

```bash
Rscript -e 'install.packages("jsonlite", repos="https://cloud.r-project.org/")'
```

## How It Works

The plugin registers a tool named `r_demo_stats` with `confirm_always` risk level. When the tool is invoked, the `ExternalExecutor` runs `run.R` as a subprocess, passes the parameters as a JSON string to `stdin`, and returns the JSON output printed to `stdout`.
