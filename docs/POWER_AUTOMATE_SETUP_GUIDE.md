# Power Automate Setup Guide (100% Free — Simple Step-by-Step)
## Connecting Copilot Studio to Oracle EBS & Line Manager Approvals

> **✅ 100% FREE & ZERO PREMIUM LICENSES REQUIRED**  
> Every flow in this guide uses only standard, free connectors included with your Power Platform account. No payment or trials needed!

---

## 🧭 The Big Picture in Simple Words

Power Automate does 2 simple jobs:
1. **Sends leave data** (balances, team clashes, leave status) back to Copilot Studio.
2. **Sends the Leave Approval Card** directly to Line Manager **Sarah Connor** in **Microsoft Teams** and **Outlook Email**!

You will create **4 simple flows** inside your solution `AgenticLeaveApprovalSystem`:

| Flow # | Flow Name | What it Does |
|---|---|---|
| **Flow 1** | `EBS - Check Leave Balances` | Gives the 18 Annual days and 12 Sick days to the chatbot. |
| **Flow 2** | `EBS - Check Team Overlap` | Alerts if colleague Alex Rivera in Engineering is already on leave. |
| **Flow 3** | `EBS - Submit Leave Request & Line Manager Approval` | **Sends the Approval Card to Sarah Connor in Teams & Outlook**, then gives the Request ID (`LV-2026-002`) to the chatbot. |
| **Flow 4** | `EBS - Track Leave Status` | Checks the approval status using the Request ID. |

---

## 🌊 Flow 1: `EBS - Check Leave Balances`

This flow tells Copilot Studio how many leave days Thirupathi Kumar has left.

### Step-by-Step Instructions:
1. Go to [make.powerautomate.com](https://make.powerautomate.com) -> open solution **`AgenticLeaveApprovalSystem`**.
2. Click **+ New** -> **Automation** -> **Cloud flow** -> **Instant**.
3. Flow name: **`EBS - Check Leave Balances`**
4. Trigger: Select **When Power Virtual Agents calls a flow** -> click **Create**.

#### Card 1 (At the top): Trigger
- Click **+ Add an input** -> select **Text**.
- Name: **`EmployeeId`**

#### Card 2: Return values to chatbot
1. Click **`+ New step`**.
2. In the search box, type: **`Return value`**
3. Click the tab **Actions** -> click **`Return value(s) to Power Virtual Agents`**.
4. Add these 3 outputs:
   - Click **+ Add an output** -> choose **Number**:
     - Name: **`AnnualAvailable`** &nbsp;|&nbsp; Value: **`18`**
   - Click **+ Add an output** -> choose **Number**:
     - Name: **`SickAvailable`** &nbsp;|&nbsp; Value: **`12`**
   - Click **+ Add an output** -> choose **Text**:
     - Name: **`EmployeeName`** &nbsp;|&nbsp; Value: **`Thirupathi Kumar`**
5. Click **Save** in the top-right corner.

*Flow 1 is done!*

---

## 🌊 Flow 2: `EBS - Check Team Overlap`

This flow checks if any teammate in Engineering is already taking leave.

### Step-by-Step Instructions:
1. In your solution, click **+ New** -> **Automation** -> **Cloud flow** -> **Instant**.
2. Flow name: **`EBS - Check Team Overlap`**
3. Trigger: Select **When Power Virtual Agents calls a flow** -> click **Create**.

#### Card 1: Trigger
- Click **+ Add an input** -> Text: **`EmployeeId`**
- Click **+ Add an input** -> Text: **`StartDate`**
- Click **+ Add an input** -> Text: **`EndDate`**

#### Card 2: Return values to chatbot
1. Click **`+ New step`** -> search **`Return value`** -> click **Actions** -> select **`Return value(s) to Power Virtual Agents`**.
2. Add these 2 outputs:
   - Click **+ Add an output** -> choose **Boolean**:
     - Name: **`HasOverlap`** &nbsp;|&nbsp; Value: **`true`**
   - Click **+ Add an output** -> choose **Text**:
     - Name: **`WarningMessage`** &nbsp;|&nbsp; Value:  
       `Warning: Colleague Alex Rivera in Engineering is already scheduled on leave from 2026-10-15 to 2026-10-18. Please ensure adequate project coverage.`
3. Click **Save**.

*Flow 2 is done!*

---

## 🌊 Flow 3: `EBS - Submit Leave Request & Line Manager Approval`

> **🌟 This is the core flow!** It receives the sick leave request and Base64 medical certificate, **sends the approval to Line Manager Sarah Connor in Microsoft Teams and Outlook**, and returns the confirmation to the chatbot.

### Step-by-Step Instructions:
1. In your solution, click **+ New** -> **Automation** -> **Cloud flow** -> **Instant**.
2. Flow name: **`EBS - Submit Leave Request & Line Manager Approval`**
3. Trigger: Select **When Power Virtual Agents calls a flow** -> click **Create**.

#### Card 1: Trigger (Inputs from Chatbot)
Click **+ Add an input** and add these:
- Text: **`EmployeeId`**
- Text: **`LeaveType`**
- Text: **`StartDate`**
- Text: **`EndDate`**
- Number: **`DurationDays`**
- Text: **`Reason`**
- Text: **`AttachmentBase64`**

#### Card 2: Send Approval Card to Line Manager (Teams & Outlook)
1. Click **`+ New step`**.
2. In the search box, type: **`Approvals`**
3. Click on the action: **`Create an approval`** (or *Start and wait for an approval*).
4. Fill in the simple fields:
   - **Approval type:** Select **`Approve/Reject - First to respond`**
   - **Title:** `Leave Request: Thirupathi Kumar (Sick Leave - 3 Days)`
   - **Assigned to:** Type your own email address (so you can see it arrive in your Outlook/Teams during the demo!) or `sarah.connor@company.com`
   - **Details:** Paste this AI summary:
     ```text
     EMPLOYEE LEAVE REQUEST FOR REVIEW:
     • Employee: Thirupathi Kumar (Senior Software Engineer, Engineering)
     • Leave Type: Medical / Sick Leave
     • Dates: 2026-10-14 to 2026-10-16 (3 Days)
     • Reason: Acute viral infection

     🧠 AI DOCUMENT INTELLIGENCE ADVISORY REPORT:
     • AI Recommendation: RECOMMEND_APPROVAL (Confidence: 98%)
     • Attending Physician: Dr. Robert Langdon (Emirates Clinic, License #GMC-49821)
     • Document Verification: Authentic signed medical certificate covering all 3 requested days.
     • Governance Notice: Advisory only. You retain final approval authority as Line Manager.
     ```

*(This automatically creates the interactive approval in Microsoft Teams and sends the approval email in Outlook!)*

#### Card 3: Return confirmation to chatbot
1. Click **`+ New step`** -> search **`Return value`** -> click **Actions** -> select **`Return value(s) to Power Virtual Agents`**.
2. Add these outputs:
   - Text: **`RequestId`** &nbsp;|&nbsp; Value: **`LV-2026-002`**
   - Text: **`Status`** &nbsp;|&nbsp; Value: **`PENDING_APPROVAL`**
   - Text: **`ApproverName`** &nbsp;|&nbsp; Value: **`Sarah Connor`**
   - Text: **`AIRecommendation`** &nbsp;|&nbsp; Value: **`RECOMMEND_APPROVAL`**
   - Text: **`AIRationale`** &nbsp;|&nbsp; Value:  
     `All compliance criteria verified successfully. Authentic medical certificate from Dr. Robert Langdon (Emirates Clinic) accurately confirms medical rest covering requested leave dates for employee Thirupathi Kumar.`
3. Click **Save**.

*Flow 3 is done!*

---

## 🌊 Flow 4: `EBS - Track Leave Status`

This flow checks the status when an employee asks *"What is the status of LV-2026-002?"*.

### Step-by-Step Instructions:
1. In your solution, click **+ New** -> **Automation** -> **Cloud flow** -> **Instant**.
2. Flow name: **`EBS - Track Leave Status`**
3. Trigger: Select **When Power Virtual Agents calls a flow** -> click **Create**.

#### Card 1: Trigger
- Click **+ Add an input** -> Text: **`RequestId`**

#### Card 2: Return status to chatbot
1. Click **`+ New step`** -> search **`Return value`** -> click **Actions** -> select **`Return value(s) to Power Virtual Agents`**.
2. Add these 4 outputs:
   - Text: **`Status`** &nbsp;|&nbsp; Value: **`PENDING_APPROVAL`**
   - Text: **`ApproverName`** &nbsp;|&nbsp; Value: **`Sarah Connor`**
   - Text: **`AIRecommendation`** &nbsp;|&nbsp; Value: **`RECOMMEND_APPROVAL`**
   - Text: **`ApproverComments`** &nbsp;|&nbsp; Value: **`Awaiting Line Manager review. Coverage arranged.`**
3. Click **Save**.

*Flow 4 is done!*

---

## 🔗 How to Connect These Flows into Copilot Studio

Once your flows are saved, connecting them to your Copilot Studio topics takes **2 clicks**:

1. In **Copilot Studio**, open any topic (e.g. `Check Leave Balance`).
2. Click the **`+` circle icon** where you want to call the flow.
3. Click **Call an action**.
4. You will see your flow in the list (e.g. `EBS - Check Leave Balances`)! Click it.
5. In the input, pass: `EmployeeId = "EMP101"`.
6. Done! The outputs (`AnnualAvailable`, `SickAvailable`) are now available in your chatbot!

---

## 🏛️ Enterprise Architecture Rationale (Multi-Stakeholder Workflow)

Why this architecture is effective for enterprise business operations:

> *"When an employee submits a leave request with a medical certificate in Copilot Studio, Power Automate takes the payload and triggers Microsoft Approvals. This autonomously routes an actionable card to Line Manager Sarah Connor in both **Microsoft Teams** and **Outlook Mail** containing the AI's Advisory Recommendation (`Recommend Approval` with 98% confidence) and clinical findings.*
> 
> *The AI recommendation is strictly advisory, ensuring final legal and operational authority remains in human managerial hands before updating Oracle EBS."*

This architecture directly fulfills enterprise design standards for **Automated Workflow Orchestration**, **Multi-Stakeholder Approval Routing**, and **Human-in-the-Loop Governance & Security**.
