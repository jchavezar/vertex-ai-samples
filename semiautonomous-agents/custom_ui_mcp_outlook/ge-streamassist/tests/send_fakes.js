import puppeteer from 'puppeteer-core';

// Let's define the 60 realistic business scenarios to send
const emailScenarios = [
  // Approvals (approx. 30)
  { subject: "Approval Request: Q3 Marketing Campaign Budget", type: "Approval", category: "Budget", requested_action: "approve budget" },
  { subject: "Action Required: Approve Expense Report - John Doe Travel", type: "Approval", category: "Expense", requested_action: "approve expense report" },
  { subject: "Approval Needed: New HR Onboarding Software Subscription", type: "Approval", category: "Software", requested_action: "approve software subscription" },
  { subject: "Urgent: Approve PR #104 - Fix Memory Leak in API Gateway", type: "Approval", category: "Code Review", requested_action: "approve PR #104" },
  { subject: "Action Required: Approve Security Access for Contractor Jane Smith", type: "Approval", category: "Security", requested_action: "approve contractor access" },
  { subject: "Approval Request: Office Renovations Phase 2 Quote", type: "Approval", category: "Facilities", requested_action: "approve renovation quote" },
  { subject: "Action Required: Approve Annual Security Audit Report 2026", type: "Approval", category: "Security", requested_action: "approve security audit" },
  { subject: "Approval Needed: Travel Request to Google Cloud Summit", type: "Approval", category: "Travel", requested_action: "approve travel request" },
  { subject: "Approval Request: External Consultant SOW - Cloud Migration", type: "Approval", category: "Consulting", requested_action: "approve consultant SOW" },
  { subject: "Urgent Approval: Server Rack Hardware Procurement", type: "Approval", category: "Procurement", requested_action: "approve hardware purchase" },
  { subject: "Approval Request: Customer Success Team Offsite Plan", type: "Approval", category: "Events", requested_action: "approve offsite plan" },
  { subject: "Action Required: Approve Vendor NDA - Snowflake Integration", type: "Approval", category: "Legal", requested_action: "approve Snowflake NDA" },
  { subject: "Approval Needed: Production Deployment of Release v2.5.1", type: "Approval", category: "Release", requested_action: "approve production release" },
  { subject: "Approval Request: Social Media Strategy Proposal", type: "Approval", category: "Marketing", requested_action: "approve social media proposal" },
  { subject: "Action Required: Approve New Salary Band for Engineering Roles", type: "Approval", category: "HR", requested_action: "approve salary bands" },
  { subject: "Approval Request: Client Refund for Order #8821", type: "Approval", category: "Finance", requested_action: "approve client refund" },
  { subject: "Approval Needed: Enterprise Zoom License Upgrade", type: "Approval", category: "Software", requested_action: "approve license upgrade" },
  { subject: "Action Required: Approve New API Rate-Limiting Policy", type: "Approval", category: "Engineering", requested_action: "approve rate limit policy" },
  { subject: "Approval Request: Graphic Design Contract Renewal", type: "Approval", category: "Legal", requested_action: "approve contract renewal" },
  { subject: "Approval Needed: Q4 Hiring Plan for Product Team", type: "Approval", category: "Hiring", requested_action: "approve hiring plan" },
  { subject: "Action Required: Approve Internal DNS Server Upgrade Project", type: "Approval", category: "IT", requested_action: "approve DNS project" },
  { subject: "Approval Request: Workspace Co-working Seat License Expansion", type: "Approval", category: "Facilities", requested_action: "approve workspace seats" },
  { subject: "Approval Needed: Enterprise Password Manager Purchase", type: "Approval", category: "Security", requested_action: "approve password manager" },
  { subject: "Action Required: Approve Updated Employee Handbook Guidelines", type: "Approval", category: "HR", requested_action: "approve handbook update" },
  { subject: "Approval Request: Cloud Security Pen-Testing Scope", type: "Approval", category: "Security", requested_action: "approve pen-test scope" },
  { subject: "Approval Needed: UI Redesign Project Figma Prototype", type: "Approval", category: "Design", requested_action: "approve Figma prototype" },
  { subject: "Action Required: Approve Vendor Onboarding - Stripe Billing", type: "Approval", category: "Finance", requested_action: "approve Stripe onboarding" },
  { subject: "Approval Request: Machine Learning GPU Compute Allocation", type: "Approval", category: "Infrastructure", requested_action: "approve GPU allocation" },
  { subject: "Approval Needed: Developer Training Course Budget", type: "Approval", category: "Training", requested_action: "approve training budget" },
  { subject: "Action Required: Approve Critical Database Schema Migration Plan", type: "Approval", category: "Engineering", requested_action: "approve schema migration" },

  // Rejections (approx. 20)
  { subject: "Reject Request: Overbudget Marketing Sponsorship Proposal", type: "Reject", category: "Sponsorship", requested_action: "reject marketing proposal" },
  { subject: "Action Required: Reject Expense Report - Excessive Meal Costs", type: "Reject", category: "Expense", requested_action: "reject expense report" },
  { subject: "Reject Proposal: Unsolicited Offshore Development Pitch", type: "Reject", category: "Vendor", requested_action: "reject vendor proposal" },
  { subject: "Action Required: Reject PR #119 - Failing Integration Tests", type: "Reject", category: "Code Review", requested_action: "reject PR #119" },
  { subject: "Reject Access Request: Non-Essential AWS Root Console Access", type: "Reject", category: "Security", requested_action: "reject AWS access" },
  { subject: "Reject Request: First-Class Flights for Sales Team Travel", type: "Reject", category: "Travel", requested_action: "reject first-class request" },
  { subject: "Action Required: Reject Third-Party Analytics Tool Onboarding", type: "Reject", category: "Software", requested_action: "reject analytics onboarding" },
  { subject: "Reject Proposal: Subcontractor Rates for Q4 DevOps Project", type: "Reject", category: "Procurement", requested_action: "reject subcontractor proposal" },
  { subject: "Action Required: Reject Out-of-Scope Feature Request #992", type: "Reject", category: "Product", requested_action: "reject feature request" },
  { subject: "Reject Booking Request: Main Conference Room Weekend Event", type: "Reject", category: "Facilities", requested_action: "reject conference room booking" },
  { subject: "Action Required: Reject Outdated API Spec Draft v0.9", type: "Reject", category: "Engineering", requested_action: "reject API spec draft" },
  { subject: "Reject Request: Legacy Windows Server Maintenance Extension", type: "Reject", category: "Infrastructure", requested_action: "reject OS support extension" },
  { subject: "Action Required: Reject Incomplete Vendor Security Assessment", type: "Reject", category: "Security", requested_action: "reject security assessment" },
  { subject: "Reject Candidate Profile: Senior Data Architect Position", type: "Reject", category: "Hiring", requested_action: "reject candidate" },
  { subject: "Action Required: Reject Custom Fonts Font-License Invoice", type: "Reject", category: "Legal", requested_action: "reject font license" },
  { subject: "Reject Request: Accelerated Beta Launch Schedule Proposal", type: "Reject", category: "Release", requested_action: "reject beta schedule" },
  { subject: "Action Required: Reject Duplicate Software Subscription Request", type: "Reject", category: "Software", requested_action: "reject software subscription" },
  { subject: "Reject Proposal: Overtime Allocation for Marketing Team Project", type: "Reject", category: "Marketing", requested_action: "reject overtime allocation" },
  { subject: "Action Required: Reject Non-Compliant Vendor Laptop Request", type: "Reject", category: "IT", requested_action: "reject laptop order" },
  { subject: "Reject Proposal: Paid Marketing Partnership Campaign", type: "Reject", category: "Marketing", requested_action: "reject partnership proposal" },

  // Fakes / Casuals / General business (approx. 10)
  { subject: "Weekly Team Standup Meeting Agenda - July 17", type: "General", category: "Meeting", requested_action: "review agenda" },
  { subject: "FYI: Office Kitchen Coffee Machine Status Update", type: "General", category: "Facilities", requested_action: "read update" },
  { subject: "Welcome to SockCop Portal - Quick Start Guide", type: "General", category: "Onboarding", requested_action: "review guide" },
  { subject: "Reminder: Fill Out Security Compliance Form by Friday", type: "General", category: "Compliance", requested_action: "complete form" },
  { subject: "Newsletter: Cloud Engineering Weekly Digest - Issue 42", type: "General", category: "Newsletter", requested_action: "read digest" },
  { subject: "System Alert: Backup Successfully Completed for Prod DB", type: "General", category: "Infrastructure", requested_action: "none" },
  { subject: "Discussion: Potential Relocation of NYC Hub Office", type: "General", category: "Facilities", requested_action: "provide feedback" },
  { subject: "Announcement: Annual General Meeting Slides Uploaded", type: "General", category: "Corporate", requested_action: "view slides" },
  { subject: "Helpful Guide: Best Practices for Writing Clear API Specs", type: "General", category: "Documentation", requested_action: "read guide" },
  { subject: "System Maintenance: Planned Scheduled Network Downtime Sunday", type: "General", category: "IT", requested_action: "plan accordingly" }
];

async function run() {
  console.log("Connecting to Chrome on port 9222...");
  const browser = await puppeteer.connect({
    browserURL: 'http://localhost:9222',
    defaultViewport: null
  });

  console.log("Locating Gmail tab...");
  const pages = await browser.pages();
  const gmailPage = pages.find(p => p.url().includes('mail.google.com'));

  if (!gmailPage) {
    console.error("Gmail tab not found! Make sure you are on Gmail.");
    await browser.disconnect();
    process.exit(1);
  }

  console.log(`Found Gmail tab: ${await gmailPage.title()}`);
  await gmailPage.bringToFront();

  const recipient = "admin@sockcop.onmicrosoft.com";

  for (let i = 0; i < emailScenarios.length; i++) {
    const email = emailScenarios[i];
    console.log(`\n[${i + 1}/${emailScenarios.length}] Sending: "${email.subject}" (${email.type})`);

    try {
      // 1. Click Compose Button via page.evaluate (robust)
      const composeClicked = await gmailPage.evaluate(() => {
        const divs = Array.from(document.querySelectorAll('div[role="button"]'));
        const compose = divs.find(d => d.textContent && d.textContent.trim() === 'Compose');
        if (compose) {
          compose.click();
          return true;
        }
        return false;
      });

      if (!composeClicked) {
        throw new Error("Compose button not found or could not be clicked via evaluate");
      }

      await new Promise(r => setTimeout(r, 1500));

      // 2. Wait for Compose Box to Appear
      // Recipient box selector is 'input[peoplekit-id]' or 'input.agP' or '[name="to"]'
      const toInput = await gmailPage.waitForSelector('input[peoplekit-id], input.agP, [name="to"]', { timeout: 10000 });
      await toInput.type(recipient);
      await new Promise(r => setTimeout(r, 500));
      await gmailPage.keyboard.press('Enter');
      await new Promise(r => setTimeout(r, 500));

      // 3. Subject input selector is '[name="subjectbox"]'
      const subjectInput = await gmailPage.waitForSelector('[name="subjectbox"]', { timeout: 5000 });
      await subjectInput.type(email.subject);
      await new Promise(r => setTimeout(r, 500));

      // 4. Body content area is '[role="textbox"][aria-label="Message Body"]'
      const bodyInput = await gmailPage.waitForSelector('[role="textbox"][aria-label="Message Body"]', { timeout: 5000 });
      
      const bodyText = `Hi Admin,

This is a simulated ${email.type} scenario email for the Executive Assistant search indexing system.

Scenario Details:
- Category: ${email.category}
- Action Requested: ${email.requested_action}
- Priority: ${email.type === 'Approval' ? 'High' : 'Normal'}

Please log into the dashboard or console to ${email.requested_action} accordingly.

Best regards,
Admin Portal Agent`;

      await bodyInput.type(bodyText);
      await new Promise(r => setTimeout(r, 500));

      // 5. Click Send Button via page.evaluate
      const sendClicked = await gmailPage.evaluate(() => {
        const divs = Array.from(document.querySelectorAll('div[role="button"]'));
        // Find send button which has text Send and class aoO
        const send = divs.find(d => d.textContent && d.textContent.trim() === 'Send');
        if (send) {
          send.click();
          return true;
        }
        return false;
      });

      if (!sendClicked) {
        throw new Error("Send button not found or could not be clicked via evaluate");
      }

      // Wait a moment for sending to finish
      await new Promise(r => setTimeout(r, 2000));
      console.log(`Sent successfully!`);
    } catch (err) {
      console.error(`Error sending email [${i + 1}]:`, err.message);
      // Try to press Escape to dismiss compose box in case of error
      await gmailPage.keyboard.press('Escape');
      await new Promise(r => setTimeout(r, 1500));
    }
  }

  console.log("\nFinished sending all 60 mock scenarios!");
  await browser.disconnect();
}

run().catch(console.error);
