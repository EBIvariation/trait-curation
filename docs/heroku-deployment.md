
Step by step guide on how to deploy the app in Heroku and enable automatic pull request deployment as well.
The instructions assume that a Heroku account has been set up.


1. Create a new Heroku app via the dashboard
2. Once created, navigate to the "Deploy" tab and in the "Deployment Method" menu, select "GitHub".
3. Search for the "trait-curation" repo and click "Connect"
4. Below, in the Automatic deploys menu, select the master branch. (I would suggest leaving the "Wait for CI" box unchecked until we set up the CI)

The app should now be successfully deployed. Follow-up instructions are included in order to enable Review Apps, which automatically create a deployment instance for every new PR.

1. Navigate to the Deploy tab, in the "Add this app to a pipeline" menu.
2. Choose "Create new pipeline" and name it the same as the project
3. Moving to staging or production shouldn't matter given that this is a development environment 
4. We now have to connect the whole pipeline to GitHub as well. Navigate to Settings > Connect to GitHub and select the repository
5. Once the pipeline is created and connected to the GitHub repo, the left most column should have a "Enable Review Apps" button
5. Click it, select "Create new review apps for new pull requests automatically " and make sure to select the "Create new review apps for new pull requests automatically" option
6. Optionally, friendlier URL patterns for review apps can be chosen by navigating to Settings > Review Apps