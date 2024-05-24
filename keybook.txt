# # Create a new Jira project:
# # python3 ./jirasimplelib.py --create-project "TaskManagementSystem" "TMS"

# # To create a new Epic:
# # python3 ./jirasimplelib.py --create-epic TMS "Create Project Structure and Setup" "Create Project Structure and Setup"
# # To create a new Epic:
# # python3 ./jirasimplelib.py --create-epic TMS "Backend Development" "Backend Development"
# # To create a new Epic:
# # python3 ./jirasimplelib.py --create-epic TMS "Fronend Development" "Frontend Development"
# # To create a new Epic:
# # python3 ./jirasimplelib.py --create-epic TMS "Quality Assurance and Testing" "Quality Assurance and Testing"

# # Create a new story in a project:
# # python3 ./jirasimplelib.py --create-story TMS "create the project repository and set up necessary development environments" "create the project repository and set up necessary development environments"
# # Create a new story in a project:
# # python3 ./jirasimplelib.py --create-story TMS "develop the backend functionalities, including task creation, assignment, and tracking." "develop the backend functionalities, including task creation, assignment, and tracking."
# # Create a new story in a project:
# # python3 ./jirasimplelib.py --create-story TMS "Claire will design and develop the user interface for the TMS." "Claire will design and develop the user interface for the TMS."
# # Create a new story in a project:
# # python3 ./jirasimplelib.py --create-story TMS "Dave will thoroughly test all features and functionalities to ensure they meet the project requirements and are bug-free." "Dave will thoroughly test all features and functionalities to ensure they meet the project requirements and are bug-free."

# # Get stories for a project:
# # python3 ./jirasimplelib.py --get-stories TMS

# # To add a story to an Epic:
# # python3 ./jirasimplelib.py --add-story-to-epic EPIC_KEY STORY_KEY

# # To create a new sprint:
# # python3 ./jirasimplelib.py --create-sprint 3 Backend Development
# # To create a new sprint:
# # python3 ./jirasimplelib.py --create-sprint 3 Fronend Development
# # To create a new sprint:
# # python3 ./jirasimplelib.py --create-sprint 3 Quality Assurance and Testing

# #get-sprints-for-board
# # python3 ./jirasimplelib.py --get-sprints-for-board 3

# # Move Issues to Sprint:
# #python3 ./jirasimplelib.py --move-signle-issue ISSUE_KEY SPRINT_ID
# # Move Issues to Sprint:
# #python3 ./jirasimplelib.py --move-signle-issue ISSUE_KEY SPRINT_ID
# # Move Issues to Sprint:
# #python3 ./jirasimplelib.py --move-signle-issue ISSUE_KEY SPRINT_ID
# #start_sprint
# python3 ./jirasimplelib.py --start-sprint SPRINT_ID Summary Start_date end_date

# #complete_stories_in_sprint
# python3 ./jirasimplelib.py --complete-stories-in-sprint SPRINT_ID

# #complete_sprint
# python3 ./jirasimplelib.py --complete-sprint SPRINT_ID Start_date end

# #sprint_report
# python3 ./jirasimplelib.py --sprint-report SPRINT_ID TMS

# # Delete all stories in a project:
# # python3 ./jirasimplelib.py --delete-all-stories TMS

# #delete_all_sprints
# python3 ./jirasimplelib.py --delete-all-sprints 3

# #delete-all-projects
# python3 ./jirasimplelib.py --delete-all-projects


# # Delete all projects:
# # python your_script.py --config path/to/config.json --delete-projects


# # To update the status of a story:
# # python your_script.py --config path/to/config.json --update-story-status STORY_KEY NEW_STATUS

# # To update the summary of a story:
# # python your_script.py --config path/to/config.json --update-story-summary STORY_KEY NEW_SUMMARY

# # To update the description of a story:
# # python your_script.py --config path/to/config.json --update-story-description STORY_KEY NEW_DESCRIPTION

# # To add comments to issues in a range:
# # python your_script.py --config path/to/config.json --add-comment-start START_ISSUE_NUM --add-comment-end END_ISSUE_NUM --add-comment-body "Comment Body"


# # To read details of a story:
# # python your_script.py --config path/to/config.json --read-story-details STORY_KEY


# # To list all Epics in a project:
# # python your_script.py --config path/to/config.json --list-epics --project-key PROJECT_KEY

# # To update an Epic:
# # python your_script.py --config path/to/config.json --update-epic EPIC_KEY NEW_SUMMARY NEW_DESCRIPTION

# # To read details of an Epic:
# # python your_script.py --config path/to/config.json --read-epic-details EPIC_KEY

# # Delete a story:
# # python your_script.py --config path/to/config.json --delete-story STORY_KEY


# # To unlink a story from an Epic:
# # python your_script.py --config path/to/config.json --unlink-story-from-epic STORY_KEY

# # To delete an Epic:
# # python your_script.py --config path/to/config.json --delete-epic EPIC_KEY


# # To get all sprints for the specified board:
# # python your_script.py --config path/to/config.json --get-sprints-for-board BOARD_ID

# # Move Issues to Sprint:
# # move_issues_to_sprint(jira, 'PROJECT', 'ISSUE-1', 'ISSUE-5', 'SPRINT_ID')

# # Start Sprint:
# # start_sprint(jira, 'SPRINT_ID', 'New Sprint Summary', '2024-03-01', '2024-03-15')


# # Get Stories in Sprint:
# # get_stories_in_sprint(jira, 'SPRINT_ID')

# # Complete Stories in Sprint:
# # complete_stories_in_sprint(jira, 'SPRINT_ID')

# # Complete Sprint:
# # complete_sprint(jira, 'SPRINT_ID', '2024-03-01', '2024-03-15')

# # Update Sprint Summary:
# # update_sprint_summary(jira, 'SPRINT_ID', 'New Sprint Summary', 'active', '2024-03-01', '2024-03-15')

# # Sprint Report:
# # sprint_report(jira, 'SPRINT_ID', 'PROJECT_KEY')

# # Get Velocity:
# # completed_velocity, total_velocity = get_velocity(jira, 'PROJECT_KEY')
# # if completed_velocity is not None and total_velocity is not None:
# #     print("Completed Velocity:", completed_velocity)
# #     print("Total Velocity:", total_velocity)


# # Delete Sprint:
# # delete_sprint(jira, 'SPRINT_ID')

# # Delete All Sprints:
# # delete_all_sprints(jira, 'BOARD_ID')

# # Create Board:
# # create_board('JIRA_URL', 'API_TOKEN', 'USER_EMAIL', 'PROJECT_KEY', 'PROJECT_LEAD')

# # Get Board ID:
# # board_id = get_board_id(jira, 'BOARD_NAME')
# # if board_id:
# #     print("Board ID:", board_id)
