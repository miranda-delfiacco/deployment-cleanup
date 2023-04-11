# Deployment-cleanup

1. Where should we run this script? 
    - (Preferred) As a cronjob in an EKS (kubernetes) cluster
    - using an eventbridge rule with a cron schedule to run an ECS task
    - using an eventbridge rule with a cron schedule to run a lambda function
2. How should we test the script before running it production?
    - ideally in a development environment / account with a similarly setup S3 bucket, we could make the bucket name a parameter as well
    - alternatively, the script has an extra 'debug' param that will only log the list of keys that would be removed in normal mode
3. If we want to add an additional requirement of deleting deploys older than 30 days while keeping X deployments. What additional changes would you need to make in the script?
    - I'd probably add something like the following (and another param to the script):
    ```
    # Get a list of the last X deployments to keep
    aws s3api list-objects-v2 --bucket <bucket> --query 'sort_by(Contents, &LastModified)[*].Key' | jq -r '.[]' | cut -d'/' -f1 | uniq | tail -<num_of_items_to_keep>
    ```
    - Remove the keys / deployments from $objects_to_delete variable
    - Continue script operation as normal

# Assumptions
- Assumes the bucket doesn't have an extremely large number of objects.  At a certain point, we'd likely need to paginate over the list of objects and rather than iterating over each deployment folder / key to remove, use the `aws s3api delete-objects...` command to delete multiple objects in a single request.  I went with `aws s3 rm` since it was easier to implement a 'debug mode' option in the script since the s3api commands don't have a `--dryrun` option
- Assumes objects within a deployment folder are of the same age
- Assumes the S3 bucket doesn't have versioning enabled