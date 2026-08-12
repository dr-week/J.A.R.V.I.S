#!/usr/bin/env Rscript

# Read stdin
input_json <- paste(readLines("stdin", warn = FALSE), collapse = "")

if (nchar(input_json) == 0) {
  cat('{"error": "No input provided"}\n')
  quit(status = 1)
}

# Try loading jsonlite
if (!requireNamespace("jsonlite", quietly = TRUE)) {
  cat('{"error": "jsonlite package is not installed. Please install it."}\n')
  quit(status = 1)
}

# Parse input
parsed <- tryCatch({
  jsonlite::fromJSON(input_json)
}, error = function(e) {
  cat(paste0('{"error": "Invalid JSON input: ', e$message, '"}\n'))
  quit(status = 1)
})

# Process data - expected parameter: numbers (array of numbers)
if (is.null(parsed$numbers) || !is.numeric(parsed$numbers)) {
  cat('{"error": "Parameter \'numbers\' must be an array of numeric values."}\n')
  quit(status = 1)
}

nums <- parsed$numbers

result <- list(
  mean = mean(nums),
  median = median(nums),
  sd = sd(nums),
  min = min(nums),
  max = max(nums),
  count = length(nums)
)

output_json <- jsonlite::toJSON(result, auto_unbox = TRUE)
cat(output_json, "\n")
