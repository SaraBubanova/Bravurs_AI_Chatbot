# Bravurs_AI_Chatbot
Branch Structure and Workflow This repository follows a structured branching strategy to manage development, testing, and deployment in a Scrum environment. Below is an overview of the branches and their roles:

### feature branches:

- Used by individual for assigned tasks from scrum master.
- Created from develop branch for new work, where initial development and commits occur.
- Merged into main after completion via pull request (PR) with code review & test.

### develop:

- Integration branch for combining feature branches.
- Used for preliminary reviews, integration checks, and basic testing (e.g., unit tests).
- Developers ensure features work together before moving to test.

### main (Default Branch):

- Represents the stable, production-ready code deployed to users.
- Only receives merges from test after successful validation.
- Protected to prevent direct pushes; updates occur via pull requests.
