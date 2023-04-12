# Deployment-cleanup

1. Where should we run this script? 
    - (Preferred) As a cronjob in an EKS (kubernetes) cluster
    - using an eventbridge rule with a cron schedule to run an ECS task
    - using an eventbridge rule with a cron schedule to run a lambda function
2. How should we test the script before running it production?
    - ideally in a development environment / account with a similarly setup S3 bucket.
    - alternatively, the script has a debug param that will only log the list of keys that would be removed in normal mode
3. If we want to add an additional requirement of deleting deploys older than 30 days while keeping X deployments. What additional changes would you need to make in the script?
    - Add a new function and argument to gather the list of deployments to keep
    - Remove that list from the parent_folders set so that they are not removed


# Assumptions
- Assumes objects within a deployment folder are of the same age
- Assumes the S3 bucket doesn't have versioning enabled
- Assumes there isn't a large (over 1000) number of objects within a parent "folder"