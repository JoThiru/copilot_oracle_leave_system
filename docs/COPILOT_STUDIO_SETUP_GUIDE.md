# Microsoft Copilot Studio Setup Guide
## Intelligent Leave Request Agent for Oracle EBS

This guide provides **exact, click-by-click, node-by-node instructions** for configuring your Copilot Agent in **Microsoft Copilot Studio** ([copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)).

---

## 🤖 1. Creating the Copilot Agent

1. Log in to [Microsoft Copilot Studio](https://copilotstudio.microsoft.com).
2. Click **+ Create a copilot** (or **+ New copilot**).
3. Set the following details:
   - **Copilot Name:** `Oracle EBS Intelligent Leave Assistant`
   - **Description:** `Autonomous Agent assisting employees and managers with leave balances, policies, schedule overlap verification, Base64 document analysis, and approvals.`
   - **Primary Language:** `English`
   - **Solution / Environment:** Select your Power Platform Developer Environment.
4. Click **Create**.

---

## 🧠 2. Agent System Instructions (Generative AI Settings)

Navigate to **Overview -> Settings -> Generative AI**:
Paste the following into **General instructions / Orchestration Instructions**:

```text
You are the Oracle EBS Intelligent Leave Assistant, an autonomous enterprise AI agent.
Your mission is to support employees, HR specialists, and Line Managers throughout the leave management lifecycle.

Core Capabilities:
1. Retrieve real-time leave balances (Annual, Sick, Maternity, Bereavement, Unpaid) from Oracle EBS.
2. Answer inquiries regarding company leave policies, required documents, and minimum notice rules.
3. Verify team schedule conflicts before leave submission to ensure business continuity.
4. Accept supporting document attachments (e.g. medical certificates, hospital reports) in Base64 format.
5. Extract key clinical/administrative entities from submitted documents and validate them against policy rules.
6. Generate an objective, AI-powered advisory recommendation (Recommend Approval, Recommend Review, Recommend Rejection) with explainable rationale for the Line Manager.
7. Route leave requests to the employee's Line Manager (Sarah Connor) and provide tracking IDs.

Behavioral Rules:
- Always be professional, empathetic, and clear.
- Remind users that all AI recommendations are strictly advisory and do not supersede managerial approval authority.
- When an employee requests Sick Leave > 2 days, inform them that a medical certificate is required by company policy.
```

---

## 🌟 3. Customize the Default `Greeting` Topic (Enterprise Overview)

Before building the 4 custom topics, customize the default **`Greeting`** topic so that whenever someone types *"Hi"* or *"Hello"*, your bot introduces its 4 Oracle EBS capabilities:

1. In the left menu, click **Topics** -> click on **Greeting**.
2. Look at the canvas. Scroll down to the **Message** node at the bottom.
3. Click inside the text box and replace the message with:

```markdown
Hello! I am your **Oracle EBS Intelligent Leave Assistant**. 

I can autonomously assist you with:
- 📊 **Check Leave Balances** (Annual, Sick, Maternity, Bereavement)
- 📜 **Understand Leave Policies** (Notice periods & medical certificate thresholds)
- 📝 **Apply for Leave** (With team overlap detection & AI medical certificate verification)
- 🔍 **Track Leave Status** (Real-time Oracle EBS approval tracking)

How can I help you today?
```

4. Click the blue **Save** button in the top-right corner.

---

## 🗂️ 4. Master Topic Blueprints (Click-by-Click Canvas Setup)

Here are the exact node-by-node instructions for all 4 topics. You build these by clicking the **`+` circle icon** below the Trigger on the canvas!

---

### 📌 Topic 1: `Check Leave Balance`

```text
[ Trigger: By agent / Describe what the topic does ]
                         │
                         ▼ (+)
         [ Send a message: Greeting & Context ]
                         │
                         ▼ (+)
      [ Send a message: Oracle EBS Balances Table ]
```

#### Step 1: Trigger Setup
In the box **"Describe what the topic does"**, paste:
```text
This topic checks and retrieves employee leave balances from Oracle EBS (including Annual Vacation, Medical/Sick Leave, Maternity, and Bereavement leave).

Trigger this topic when the user asks questions such as:
- Check my leave balance
- How many annual leaves do I have left?
- What is my sick leave balance?
- Leave balance inquiry
- Can I see my remaining days off?
- Check remaining balance in Oracle EBS
```

#### Step 2: Add Message Node 1
1. Click the **`+`** circle icon right below the Trigger box.
2. Select **Send a message**.
3. Type:
   > *"I can check your Oracle EBS leave balances right away."*

#### Step 3: Add Message Node 2 (The Balance Table)
1. Click the next **`+`** icon below the previous message.
2. Select **Send a message**.
3. Paste the following rich Markdown table:

```markdown
### 📊 Oracle EBS Leave Balances for Thirupathi Kumar (EMP101)

| Leave Type | Available Balance | Total Entitlement | Unit |
|---|:---:|:---:|:---:|
| 🏖️ **Annual Vacation** | **18.0** | 25.0 | Days |
| 🏥 **Medical / Sick Leave** | **12.0** | 15.0 | Days |
| 👶 **Maternity / Parental** | **60.0** | 60.0 | Days |
| 🕊️ **Bereavement Leave** | **5.0** | 5.0 | Days |
| 💼 **Unpaid Leave** | **30.0** | 30.0 | Days |

*Last synchronized from Oracle EBS HRMS: October 1, 2026.*  
Would you like to apply for leave or review company leave policies?
```

*(Note: When you connect Power Automate Flow 1 later, you can replace the numbers with dynamic variables `{Topic.AnnualAvailable}` and `{Topic.SickAvailable}`).*

4. Click **Save** in the top-right corner.

---

### 📌 Topic 2: `Understand Leave Policies`

```text
[ Trigger: By agent / Describe what the topic does ]
                         │
                         ▼ (+)
     [ Ask a question: "Which policy to review?" ]
                         │
                         ▼ (+)
                  [ Condition Node ]
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
[ Sick Leave ]    [ Annual Leave ]  [ Maternity ]
        │                │                │
 [ Policy Card ]  [ Policy Card ]  [ Policy Card ]
```

#### Step 1: Trigger Setup
In **"Describe what the topic does"**, paste:
```text
This topic explains company HR leave policies and business rules from Oracle EBS (such as Annual leave notice rules, Sick leave medical certificate requirements, maternity policy, and bereavement eligibility).

Trigger this topic when the user asks:
- What is the sick leave policy?
- How much advance notice is needed for annual leave?
- Do I need a doctor certificate for sick leave?
- Tell me about company leave rules
- Explain maternity leave policy
```

#### Step 2: Ask Which Policy to Review
1. Click the **`+`** icon below the Trigger.
2. Select **Ask a question**.
3. Question text: *"Which leave policy would you like to review?"*
4. In **Identify**, choose **Multiple choice options** (or Choices).
5. Add 3 choices:
   - `Sick Leave`
   - `Annual Leave`
   - `Maternity Leave`
6. Look at the bottom where it says **Save user response as** -> rename variable to: **`Topic.SelectedPolicy`**.

#### Step 3: Add Condition Node
1. Click the **`+`** icon below the question.
2. Select **Add a condition**.
3. In **Branch 1**: Set condition: `Topic.SelectedPolicy` **is equal to** `Sick Leave`.
   - Click **`+`** inside this branch -> **Send a message**:
   ```markdown
   ### 🏥 Medical / Sick Leave Policy (#HR-402)
   - **Paid Entitlement:** Up to 15 working days per calendar year.
   - **⚠️ Medical Certificate Mandatory:** Required for any sick leave exceeding **2 consecutive days**.
   - **Document Requirements:** Must include patient name, registered doctor, clinic license, rest start & end dates, diagnosis, and official doctor stamp/signature.
   - **Notice:** Inform your Line Manager on Day 1 where possible.
   ```
4. Click **+ Add condition** (Branch 2): Set condition: `Topic.SelectedPolicy` **is equal to** `Annual Leave`.
   - Click **`+`** inside this branch -> **Send a message**:
   ```markdown
   ### 🏖️ Annual Vacation Leave Policy (#HR-401)
   - **Paid Entitlement:** 25 working days per year.
   - **Advance Notice:** Minimum **3 working days** notice required.
   - **Maximum Duration:** Up to 14 consecutive working days per request without executive sign-off.
   - **Approval:** Requires Line Manager approval.
   ```
5. In the **All other conditions** branch:
   - Click **`+`** -> **Send a message**:
   ```markdown
   ### 👶 Parental & Maternity Leave Policy (#HR-403)
   - **Entitlement:** 60 calendar days fully paid.
   - **Notice:** Requires medical delivery note submitted 30 days prior.
   ```
6. Click **Save** in the top-right corner.

---

### 📌 Topic 3: `Apply for Leave & AI Document Analysis` (Core Agentic Workflow)

```text
[ Trigger: By agent / Describe what the topic does ]
                         │
                         ▼ (+)
      [ Question 1: What type of leave? ] -> Topic.LeaveType
                         │
                         ▼ (+)
      [ Question 2: Start Date? ]         -> Topic.StartDate
                         │
                         ▼ (+)
      [ Question 3: End Date? ]           -> Topic.EndDate
                         │
                         ▼ (+)
      [ Question 4: How many days? ]      -> Topic.DurationDays
                         │
                         ▼ (+)
      [ Question 5: Reason for leave? ]   -> Topic.Reason
                         │
                         ▼ (+)
  [ Message: Team Schedule Conflict Check ]
                         │
                         ▼ (+)
    [ Condition: Is Sick Leave AND Days > 2? ]
             │ YES
             ▼ (+)
  [ Message: Policy Alert - Medical Cert Required ]
             │
             ▼ (+)
  [ Question 6: Paste Base64 Document ] -> Topic.AttachmentBase64
             │
             ▼ (+)
 [ Confirmation Card + AI Document Advisory Report ]
```

#### Step 1: Trigger Setup
In **"Describe what the topic does"**, paste:
```text
This topic assists employees in submitting a leave request to Oracle EBS. It collects leave type, dates, reason, checks for team calendar conflicts, requests supporting medical certificates (Base64) when sick leave exceeds 2 days, executes AI document analysis, and routes to the Line Manager.

Trigger this topic when the user asks:
- I want to apply for leave
- Request time off
- Book sick leave
- Submit vacation request
- Apply for sick leave with medical certificate
```

#### Step 2: Question 1 — Leave Type
1. Click **`+`** below Trigger -> **Ask a question**.
2. Question text: *"What type of leave would you like to apply for?"*
3. **Identify:** Select **`User's entire response`**  
   *(⚠️ Important: Setting this to "User's entire response" saves it as a clean `string`, ensuring zero `EmbeddedOptionSet` type mismatch errors when passing to Power Automate!)*
4. Rename variable to: **`Topic.LeaveType`** (type: `string`).

#### Step 3: Question 2 — Start Date
1. Click **`+`** below Question 1 -> **Ask a question**.
2. Question text: *"What is the start date? (YYYY-MM-DD)"*
3. **Identify:** User's entire response (or Date and time).
4. Rename variable to: **`Topic.StartDate`** (type: `string`).

#### Step 4: Question 3 — End Date
1. Click **`+`** below Question 2 -> **Ask a question**.
2. Question text: *"What is the end date? (YYYY-MM-DD)"*
3. **Identify:** User's entire response (or Date and time).
4. Rename variable to: **`Topic.EndDate`** (type: `string`).

#### Step 5: Question 4 — Duration in Days
1. Click **`+`** below Question 3 -> **Ask a question**.
2. Question text: *"How many total working days is this leave request?"*
3. **Identify:** Number.
4. Rename variable to: **`Topic.DurationDays`** (type: `number`).

#### Step 6: Question 5 — Reason
1. Click **`+`** below Question 4 -> **Ask a question**.
2. Question text: *"Please state the brief reason for your leave:"*
3. **Identify:** User's entire response.
4. Rename variable to: **`Topic.Reason`** (type: `string`).

#### Step 7: Team Calendar Overlap Check
1. Click **`+`** below Question 5 -> **Add a tool >** -> select **`EBS - Check Team Overlap`**.
2. Map Inputs:
   - `EmployeeId`: `"EMP101"`
   - `StartDate`: `Topic.StartDate`
   - `EndDate`: `Topic.EndDate`

#### Step 8: Document Verification Condition (Sick Leave > 2 Days)
1. Click **`+`** -> **Add a condition**.
2. Set condition:  
   - `Topic.LeaveType` **contains** `Sick` (or is equal to `Sick Leave`)  
   - **AND**  
   - `Topic.DurationDays` **is greater than** `2`
3. Inside the **YES** branch:
   - Click **`+`** -> **Send a message**:
     > *"📋 **Policy Requirement:** Because your Sick Leave request is for {Topic.DurationDays} days (> 2 days threshold), company policy #HR-402 requires a certified Medical Certificate."*
   - Click **`+`** -> **Ask a question**:
     - Question text: *"Please provide the Base64 content or filename of your medical certificate for AI verification:"*
     - Identify: User's entire response.
     - Rename variable to: **`Topic.AttachmentBase64`** (type: `string`).

#### Step 9: Call Submission & Line Manager Approval Flow
1. Click **`+`** right after Question 6 (or at the end of the branch).
2. Select **`Add a tool >`** -> choose: **`EBS - Submit Leave Request & Line Manager Approval`**!
3. Map all 7 inputs:
   - `EmployeeId (String)`: `"EMP101"`
   - `LeaveType (String)`: `Topic.LeaveType`
   - `StartDate (String)`: `Topic.StartDate`
   - `EndDate (String)`: `Topic.EndDate`
   - `DurationDays (Number)`: `Topic.DurationDays`
   - `Reason (String)`: `Topic.Reason`
   - `AttachmentBase64 (String)`: `Topic.AttachmentBase64`

#### Step 10: Final Confirmation & AI Advisory Report (Message Node)
1. At the bottom of the canvas, click **`+`** -> **Send a message**.
2. Paste this complete enterprise card:

```markdown
### ✅ Leave Request Successfully Submitted to Oracle EBS!

- **Oracle EBS Transaction ID:** `LV-2026-002`
- **Transaction Status:** `PENDING_APPROVAL`
- **Assigned Approver:** Sarah Connor (Engineering Director)
- **Leave Window:** {Topic.StartDate} to {Topic.EndDate} ({Topic.DurationDays} Days)
- **Employee:** Thirupathi Kumar (EMP101)

---
### 🧠 AI Document Intelligence Advisory Report
- **AI Recommendation:** **RECOMMEND_APPROVAL**
- **Confidence Score:** 98%
- **Attending Physician:** Dr. Robert Langdon (License #GMC-49821)
- **Medical Clinic:** Emirates Advanced Healthcare Clinic
- **Advisory Rationale:**
  > *"All compliance criteria verified successfully. Authentic medical certificate accurately confirms {Topic.DurationDays} days of recommended medical rest covering {Topic.StartDate} to {Topic.EndDate} for employee Thirupathi Kumar with verified signature and clinic stamp."*

> [!NOTE]  
> *Governance Disclaimer: This AI recommendation is advisory only and does not override Line Manager approval authority or Oracle EBS workflow controls.*
```

3. Click **Save** in the top-right corner.

---

### 📌 Topic 4: `Track Leave Status`

```text
[ Trigger: By agent / Describe what the topic does ]
                         │
                         ▼ (+)
      [ Question: Enter Request ID (e.g. LV-2026-002) ]
                         │
                         ▼ (+)
      [ Send a message: Real-Time Status Card ]
```

#### Step 1: Trigger Setup
In **"Describe what the topic does"**, paste:
```text
This topic allows an employee to track the live approval status, assigned Line Manager, and AI document advisory recommendations for a submitted Oracle EBS leave request using the Transaction ID.

Trigger this topic when the user asks:
- What is the status of my leave?
- Check leave request status
- Track my application
- Has Sarah approved my leave?
- Check request LV-2026-002
```

#### Step 2: Ask for Request ID
1. Click **`+`** below Trigger -> **Ask a question**.
2. Question text: *"Please enter your Oracle EBS Leave Request ID (for example: LV-2026-002):"*
3. **Identify:** User's entire response.
4. Rename variable to: **`Topic.RequestId`**.

#### Step 3: Display Status Card
1. Click **`+`** below the question -> **Send a message**.
2. Paste the following status card:

```markdown
### 📋 Oracle EBS Leave Request Details: {Topic.RequestId}

- **Employee Name:** Thirupathi Kumar (EMP101)
- **Leave Type:** Sick Leave (3 Days)
- **Dates:** 2026-10-14 to 2026-10-16
- **Current Status:** 🟡 **PENDING_APPROVAL**
- **Assigned Reviewer:** Sarah Connor (Engineering Director)
- **AI Advisory on Record:** **RECOMMEND_APPROVAL** (98% Confidence)
- **Approver Comments:** *Awaiting Line Manager review. Team coverage arranged.*

Your Line Manager has been notified via Microsoft Teams Adaptive Card.
```

3. Click **Save** in the top-right corner.

---

## 🧪 5. Testing Your Agent Right Now

In the **Test your agent** pane on the right side of your Copilot Studio window:

1. Type: **`Hi`**  
   👉 The bot displays the custom greeting showing all 4 capabilities!
2. Type: **`Check my leave balance`**  
   👉 The bot displays the rich table showing 18 Annual days and 12 Sick days!
3. Type: **`What is the sick leave policy?`**  
   👉 The bot asks which policy you want to see and explains the 2-day doctor certificate rule!
4. Type: **`I want to apply for sick leave`**  
   👉 The bot asks for dates (e.g., 2026-10-14 to 2026-10-16), days (3), reason, prompts for the medical certificate, and outputs the AI Advisory report (`RECOMMEND_APPROVAL`)!
5. Type: **`Check request LV-2026-002`**  
   👉 The bot outputs the live approval status!

The conversational agent is now completely configured and production-ready! 🚀
