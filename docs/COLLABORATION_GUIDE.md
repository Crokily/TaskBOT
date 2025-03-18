# Collaboration Guide

Welcome to the TaskBOT project! This guide provides detailed instructions on how to collaborate using GitHub, including how to claim tasks, update task statuses, develop and submit code via Pull Requests (PRs). Please read carefully and follow the outlined processes.

---

## 1. Task Management Process

### 1.1 How to View and Claim Tasks
1. **View Tasks**:
   - Open the GitHub Issues page: https://github.com/AISoc-UNSW/TaskBOT/issues
   - Tasks are listed as Issues, e.g., `Issue 1: Discord Bot Management Page UI Prototype Design`.
   - Alternatively, check the **Projects** page: https://github.com/AISoc-UNSW/TaskBOT/projects
     - Tasks are assigned to the `To Do` column on the board.

1. **Claim Tasks**:
   - Find a task you want. Open the issue and assign yourself by clicking your avatar under **Assignees**.
   - After claiming, drag the Issue from `To Do` to `In Progress` on the board to indicate you’ve started working.
   - Once finished, move it to **Done** and add a quick comment in the issue.
> 	⚠️ **Note:**
> 	- Ideally, each issue should be claimed by 1–2 people.
> 	- If a task is already claimed, confirm with the Assignee if it's okay to join.

---

## 2. Code Collaboration Process

### 2.1 Setup
1. **Clone the Repository**:
   - Clone the repo to your local machine:
     ```
     git clone https://github.com/AISoc-UNSW/TaskBOT.git
     cd TaskBOT
     ```
   - Install necessary dependencies: pip install requirements.txt

2. **Configure Environment Variables**:
   - Copy environment Variables(in the discord it channel) to `.env`
   - Fill in required configurations (e.g., Discord Bot Token, Supabase keys).
   - **Note**: Do not commit the `.env` file to GitHub (already in `.gitignore`).

### 2.2 Git Branch Management
1. **Create a Branch**:
   - Each task corresponds to a branch, named following: `feature/issue-<number>-<brief-description>`.
     - E.g., Issue 1 (UI Prototype): `feature/issue-1-ui-design`
     - E.g., Issue 2 (Database Setup): `feature/issue-2-database-setup`
   - Create and switch to a new branch:
     ```
     git checkout -b feature/issue-1-ui-design
     ```

2. **Develop Code**:
   - Work on your branch, adhering to project standards (e.g., use Tailwind CSS, follow ESLint rules).
   - Avoid hardcoding sensitive data (e.g., API keys); use environment variables.

### 2.3 Commit Code
1. **Commit Changes**:
   - Stage and commit your changes:
     ```
     git add .
     git commit -m "Add UI prototype for Discord Bot management page #1"
     ```
   - Reference the Issue in the commit message, e.g., `#1`.

2. **Push to GitHub**:
   - Push your code to the remote repository:
     ```
     git push origin feature/issue-1-ui-design
     ```

### 2.4 Create a Pull Request (PR)
1. **Create PR**:
   - After pushing, GitHub will prompt you to create a PR.
   - Or manually go to **Pull requests** -> **New pull request**.
   - Select your branch (e.g., `feature/issue-1-ui-design`) and target branch (`main`).

2. **Fill PR Description**:
   - Describe your changes, e.g.:
     ```
     Completed UI prototype design for Discord Bot management page, including:
     - Login page
     - Dashboard page
     - Task details page
     Figma link: https://www.figma.com/xxx
     Related Issue: Closes #1
     ```
   - Use `Closes #1` to auto-close the Issue upon merging.

3. **Request Review**:
   - In the PR, select **Reviewers** and @ the lead or relevant team members (e.g., frontend lead) for review.

### 2.5 Code Review and Merge
1. **Await Review**:
   - Reviewers will comment on the PR with suggestions or issues.
   - You may need to address feedback.

2. **Make Changes**:
   - Continue editing locally, then commit and push updates:
     ```
     git add .
     git commit -m "Update UI based on feedback"
     git push origin feature/issue-1-ui-design
     ```
   - Changes will automatically update the PR.

3. **Merge PR**:
   - Once approved, the lead will merge the PR into `main`.
   - Delete the branch after merging (GitHub will prompt you).

---

## 3. Best Practices

### 3.1 Task Management
- **Update Regularly**: Report progress in Issues and seek help when needed.
- **Use the Board**: Keep the board status (To Do / In Progress / Done) aligned with your work.
- **Clarify Requirements**: If a task is unclear (e.g., UI design details), ask in the Issue or start a Discord thread.

### 3.2 Code Standards
- **Avoid Hardcoding**: Store sensitive data (e.g., Discord Bot Token, Supabase keys) in `.env`.
- **Commit Messages**: Keep messages clear and link to Issues, e.g., `Add database setup #2`.
- **Style Guidelines**:
  - Frontend: Use Tailwind CSS, avoid inline styles.
  - Backend: Follow RESTful API naming conventions.

### 3.3 Open Source Prep
- Ensure code is readable with clear comments.
- Avoid committing sensitive data.
- Contribute to README and docs updates.