# Load necessary library
library(dplyr)

# Load data
data <- read.csv("iss_data_3days.csv")

# Parse collected_at explicitly as UTC
data$collected_at <- as.POSIXct(data$collected_at, format="%Y-%m-%d %H:%M:%S", tz="UTC")

# Step 1: Filter out 6 Nov and 10 Nov (based on UTC time)
cleaned_data <- data %>%
  filter(!as.Date(collected_at, tz="UTC") %in% as.Date(c("2025-11-06", "2025-11-10")))

# Step 2: Add collection date column (still in UTC)
cleaned_data$date_only <- as.Date(cleaned_data$collected_at, tz="UTC")

# Sample 50% of each day's data
sampled_data <- cleaned_data %>%
  group_by(date_only) %>%
  sample_frac(0.5)

# Save cleaned + sampled dataset
write.csv(sampled_data, "iss_data_3days_sampled.csv", row.names = FALSE)

# Verify the number of records per day
sampled_data %>%
  count(date_only)

View(sampled_data)
