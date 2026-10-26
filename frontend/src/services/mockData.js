// src/services/mockData.js
// Realistic mock data and scoring engine for AI Fake Job Detection System

export const MOCK_USER = {
  id: 'usr-8821',
  name: 'Srikanth Rao',
  email: 'srikanth@riskshield.ai',
  role: 'Senior Cyber Risk Analyst',
  department: 'Threat Intelligence & Talent Security',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80',
  organization: 'Apex Cyber Intelligence',
  apiKey: 'fjd_live_key_9a7b63c2e41108a994ef03d7b8821e90',
  apiKeyCreated: '2026-08-14',
  scansUsed: 74,
  scansLimit: 150,
  plan: 'Enterprise Pro ML',
  status: 'Active',
  preferences: {
    emailAlerts: true,
    weeklyReport: true,
    autoQuarantine: false,
    strictDomainCheck: true,
  },
}

export const MOCK_KPIS = {
  totalScanned: 14892,
  fakeDetected: 3410,
  suspiciousCount: 1842,
  safeVerified: 9640,
  fraudPercentage: '22.9%',
  modelAccuracy: '97.4%',
  precisionScore: '98.1%',
  recallScore: '96.5%',
  avgInferenceTimeMs: 148,
}

export const MOCK_JOB_PRESETS = [
  {
    id: 'fake-check-scam',
    title: 'Administrative Data Entry Assistant & Invoice Processor',
    company_name: 'Apex Global Logistics LLC',
    location: 'Remote (US & Canada)',
    department: 'Administrative Operations',
    salary_range: '$45 - $55 / hr (Part-Time / Flexible)',
    contact_email: 'apex_recruitment_coordinator@gmail.com',
    company_url: 'http://apex-logistics-freecareers.com',
    category: 'Fake (Upfront Fee / Fake Check)',
    verdict: 'FRAUDULENT (94/100 Risk)',
    why_explanation: 'Classic Fake Check Overpayment Scam: Unrealistic hourly wage ($50/hr for zero experience), uses free webmail (@gmail.com) instead of corporate email, and requires depositing an advance check and wiring funds to an "equipment supplier".',
    description: `We are urgently seeking immediate Data Entry Operators to work remotely from home! No previous administrative experience required. Flexible working hours that fit your schedule.

You will be responsible for entering client shipping manifests and inventory numbers into our proprietary portal. 

IMPORTANT SETUP PROCESS: A pre-approved company cashier's check of $3,500 will be mailed to your address upon onboarding. You must deposit this check into your personal account and wire funds to our certified office hardware supplier to purchase your encrypted workstation package.`,
    requirements: `Requirements:
- Must have basic computer knowledge and typing speed of at least 35 WPM.
- Must be 18+ years old with reliable internet access.
- Must hold an active personal checking account to process the initial equipment check deposit.`,
    benefits: `Benefits:
- Fast weekly direct deposits.
- Work any 3-4 hours per day at your leisure.
- $500 sign-on bonus upon successful software setup.`,
    has_company_logo: false,
    has_questions: false,
    telecommuting: true,
  },
  {
    id: 'fake-crypto-mule',
    title: 'Financial Payment Task Specialist & Settlement Agent',
    company_name: 'Binance Global Clearing Trust',
    location: 'Remote (Worldwide)',
    department: 'Treasury & Client Settlements',
    salary_range: '$8,500 - $14,000 / month + 5% commission',
    contact_email: 'binance_hr_direct@protonmail.com',
    company_url: 'http://binance-vip-verification-task.xyz',
    category: 'Fake (Money Mule / Crypto Scheme)',
    verdict: 'FRAUDULENT (98/100 Risk)',
    why_explanation: 'Money Laundering & Mule Scam: Impersonates major exchange, conducts interviews exclusively over Telegram, asks candidates to receive third-party bank deposits and convert them to Bitcoin/USDT for 5% commission.',
    description: `URGENT VACANCY: Earn high daily income working 1-2 hours per day! We are an authorized international payment processing partner.

Your primary duty is to receive client funds into your personal account, convert them into cryptocurrency (USDT or Bitcoin) via nearest crypto ATM or P2P exchange, and forward the funds to our corporate wallet while keeping a 5% commission.

INTERVIEW PROCESS: No formal resume or interview required. All communication is conducted via Telegram. Message our Senior Recruitment Officer on Telegram @HR_FastHire_Manager to start immediately.`,
    requirements: `Requirements:
- Any individual over 18 with a personal crypto wallet or active bank account.
- Must be able to respond to Telegram instructions within 15 minutes.
- Must submit a photo of your passport/driver's license and selfie holding ID for instant identity verification.`,
    benefits: `Benefits:
- Instant daily payouts directly in cryptocurrency.
- No tax reporting required.
- $1,000 bonus on your first 5 transactions.`,
    has_company_logo: false,
    has_questions: false,
    telecommuting: true,
  },
  {
    id: 'fake-emscad-494',
    title: 'Admin Assistant / Receptionist (Immediate Start)',
    company_name: 'Newly Established Executive Firm',
    location: 'US, TX, Austin',
    department: 'General Administration',
    salary_range: '$23,040 - $28,800 / yr',
    contact_email: 'adminhireoffice2024@yahoo.com',
    company_url: '',
    category: 'Fake (Phishing & Identity Harvest)',
    verdict: 'FRAUDULENT (91/100 Risk)',
    why_explanation: 'EMSCAD #494: Anonymous entity ("Newly established company"), no company logo or URL, free Yahoo contact email, and requests direct processing of sensitive tax records and personal IDs prior to formal verification.',
    description: `A Newly established company seeks outgoing, friendly people person with a can do attitude for an Admin Assistant/Receptionist position yet to be occupied. 
Job duties include answering phones, setting appointments, scheduling client calls, and working with the owner to keep the office running smooth. 
Processing of client tax returns, keeping office clean and orderly, ordering supplies, and handling sensitive payment disbursements. Immediate hiring with expedited onboarding.`,
    requirements: `Requirements:
- High School Diploma or equivalent.
- Basic computer knowledge and outgoing attitude.
- Willingness to undergo fast-track background paperwork.`,
    benefits: `Benefits:
- Paid holidays and vacation time.
- Flexible daytime work hours.`,
    has_company_logo: false,
    has_questions: false,
    telecommuting: false,
  },
  {
    id: 'fake-emscad-358',
    title: 'Financing Auto (Car) Sales Representative',
    company_name: 'Hazelcrest Auto Credit Solutions',
    location: 'US, IL, Hazelcrest',
    department: 'Vehicle Sales & Financing',
    salary_range: '$35,000 - $73,000 / yr ($500-$1000/wk)',
    contact_email: 'carfinancerecruit@outlook.com',
    company_url: '',
    category: 'Fake (Bait-and-Switch Commission)',
    verdict: 'FRAUDULENT (88/100 Risk)',
    why_explanation: 'EMSCAD #358: Bare-bones posting lacking corporate registration or logo, promise of quick weekly cash ($500 - $1,000 a week by contract), zero vetting requirements, and free webmail.',
    description: `If you have experience in financing for auto sales and a great attitude you can work in our Hazelcrest office. From $500 up to $1000 a week by 1099 contract. 

You will handle walk-in credit applications, process customer subprime financing paperwork, and verify cash deposits. Fast turnaround on applications, start as early as tomorrow morning. Call or email our hiring coordinator directly for immediate interview slot.`,
    requirements: `Requirements:
- Motivated self-starter with good communication.
- Prior sales or phone customer service experience preferred.
- Must have personal vehicle and active checking account for contract pay.`,
    benefits: `Benefits:
- Daily and weekly performance cash bonuses.
- Flexible schedule and high commission caps.`,
    has_company_logo: false,
    has_questions: false,
    telecommuting: false,
  },
  {
    id: 'fake-emscad-538',
    title: 'Technology Consultant - Outside Sales (High Commission)',
    company_name: 'SkyNet Managed Technology Services',
    location: 'US, OH, Columbus',
    department: 'Enterprise Sales',
    salary_range: '$60,000 - $120,000 / yr',
    contact_email: 'skynet.recruitment.ohio@gmail.com',
    company_url: 'http://skynet-managed-it-services-portal.net',
    category: 'Fake (Phishing Portal & Link Redirection)',
    verdict: 'FRAUDULENT (93/100 Risk)',
    why_explanation: 'EMSCAD #538: Uses disguised application redirect link, generic corporate name impersonation, missing verifiable registry, and redirects candidates to third-party data harvesting form.',
    description: `SkyNet Managed Technology Services, a leading IT consulting firm based in Columbus, Ohio, is seeking a dynamic sales professional who can hunt, identify opportunities, and sell technology solutions and professional services to small and medium business clients. 

Candidates must apply exclusively through our external portal link to submit credit check authorization and SSN verification prior to video phone interview.`,
    requirements: `Requirements:
- 1-3 years B2B outside sales experience.
- Track record of cold calling and prospecting.
- Ability to pass immediate online third-party identity verification.`,
    benefits: `Benefits:
- High commission uncapped structure.
- Travel expense reimbursement.`,
    has_company_logo: false,
    has_questions: false,
    telecommuting: false,
  },
  {
    id: 'fake-emscad-99',
    title: 'IC&E Technician - Energy Operations',
    company_name: 'Poso Energy Operations Group',
    location: 'US, CA, Bakersfield',
    department: 'Plant Instrumentation & Electrical',
    salary_range: '$95,000 - $115,000 / yr',
    contact_email: 'energy.recruitment.poso@mail.com',
    company_url: '',
    category: 'Fake (Clone / Recruiter Impersonation)',
    verdict: 'FRAUDULENT (89/100 Risk)',
    why_explanation: 'EMSCAD #99: Cloned high-salary technical vacancy ($95k-$115k) lifted verbatim from legitimate plant listings, but stripped of real corporate branding, using free webmail (@mail.com) and unauthorized contact vectors.',
    description: `IC&E Technician | Bakersfield, CA Mt. Poso. 
Principal Duties and Responsibilities: Calibrates, tests, maintains, troubleshoots, and installs all power plant instrumentation, control systems and electrical equipment. Performs maintenance on motor control centers, motor operated valves, generators, switchgear, and PLC systems.

Applicants must submit direct wire transfer deposit for pre-employment OSHA safety equipment and drug-screening kit prior to reporting to site.`,
    requirements: `Requirements:
- 5+ years experience as an IC&E technician in a power generation or heavy industrial environment.
- Knowledge of distributed control systems (DCS) and Allen Bradley PLCs.
- Technical degree or military electrical training preferred.`,
    benefits: `Benefits:
- Premium medical, dental, vision coverage.
- Relocation assistance for qualified hires.`,
    has_company_logo: false,
    has_questions: false,
    telecommuting: false,
  },
  {
    id: 'safe-sample',
    title: 'Staff Software Engineer - Cloud Architecture',
    company_name: 'Stripe Technologies Inc.',
    location: 'San Francisco, CA (Hybrid)',
    department: 'Core Infrastructure',
    salary_range: '$210,000 - $265,000 / yr',
    contact_email: 'recruiting-engineering@stripe.com',
    company_url: 'https://stripe.com/jobs',
    category: 'Real / Legitimate',
    verdict: 'LEGITIMATE (0/100 Risk)',
    why_explanation: 'Legitimate corporate domain (@stripe.com), transparent role scope, realistic market compensation, zero upfront fee demands, standard multi-round technical interview process.',
    description: `Stripe is looking for a Staff Software Engineer to help design and implement our next-generation cloud infrastructure. You will partner with security, reliability, and payments teams to scale global distributed transaction engines with five-nines availability.

Responsibilities:
- Architect distributed systems handling trillions of dollars in annualized volume.
- Lead multi-datacenter latency optimizations and zero-downtime database migrations.
- Mentor senior engineers and drive infrastructure architectural roadmaps.`,
    requirements: `Requirements:
- 8+ years experience in distributed backend architecture (Go, Java, Rust, or C++).
- Deep expertise in Kubernetes, AWS/GCP primitives, and resilient consensus protocols.
- Excellent written documentation and technical communication skills.`,
    benefits: `Benefits:
- Competitive base salary + equity compensation.
- Comprehensive health, vision, dental, and 401(k) matching up to 6%.
- $1,500 annual home office budget and 25 days paid time off.`,
    has_company_logo: true,
    has_questions: true,
    telecommuting: false,
  },
  {
    id: 'real-analyst',
    title: 'Cybersecurity Threat Intelligence Analyst',
    company_name: 'CrowdStrike Holdings Inc.',
    location: 'Austin, TX / Remote',
    department: 'Global Threat Research',
    salary_range: '$115,000 - $145,000 / yr',
    contact_email: 'careers@crowdstrike.com',
    company_url: 'https://www.crowdstrike.com/careers',
    category: 'Real / Legitimate',
    verdict: 'LEGITIMATE (5/100 Risk)',
    why_explanation: 'Authentic enterprise posting: Uses legitimate registered corporate domain (@crowdstrike.com), detailed technical competencies, standard salary benchmarks, and official career ATS portal.',
    description: `CrowdStrike is looking for a Cybersecurity Threat Intelligence Analyst to monitor adversarial activity groups, conduct technical malware telemetry analysis, and author threat intelligence briefings for enterprise customers.

Responsibilities:
- Track nation-state and cybercrime threat actors across the MITRE ATT&CK framework.
- Correlate IOCs and malicious campaign infrastructure across global endpoints.
- Collaborate with threat hunting and reverse-engineering teams to publish actionable defense advisories.`,
    requirements: `Requirements:
- 3+ years experience in cyber threat intelligence, SOC operations, or malware analysis.
- Working knowledge of STIX/TAXII standards, SIEM queries (Splunk/ELK), and Python scripting.
- Industry certifications (GCTI, CISSP, CEH) preferred.`,
    benefits: `Benefits:
- Comprehensive medical, dental, and mental healthcare packages.
- Competitive 401(k) matching and Employee Stock Purchase Plan (ESPP).
- Flexible PTO and continuous education stipends.`,
    has_company_logo: true,
    has_questions: true,
    telecommuting: true,
  },
  {
    id: 'real-emscad-1',
    title: 'Marketing & Editorial Intern',
    company_name: 'Food52 Digital Media',
    location: 'US, NY, New York',
    department: 'Content & Community',
    salary_range: '$18 - $22 / hr',
    contact_email: 'internships@food52.com',
    company_url: 'http://www.food52.com',
    category: 'Real / Legitimate',
    verdict: 'LEGITIMATE (3/100 Risk)',
    why_explanation: 'EMSCAD #1: Verifiable digital media brand, complete company profile, verified domain and logo present, legitimate editorial screening requirements without fee demands.',
    description: `Food52, a fast-growing, James Beard Award-winning online food community and crowd-sourced recipe hub, is currently interviewing candidates for our Editorial & Marketing Internship in our New York City headquarters.

Responsibilities:
- Assisting in publishing and syndicating seasonal recipe collections.
- Curating social media feeds and engaging with our food-creator community.
- Supporting partner newsletter production and recipe metadata tagging.`,
    requirements: `Requirements:
- Enrolled in or recently graduated with a degree in Communications, English, Journalism or Marketing.
- Passionate about culinary culture and digital lifestyle journalism.
- Strong writing, copyediting, and organizational skills.`,
    benefits: `Benefits:
- College course credit or competitive hourly stipend.
- Mentorship from senior editors and test-kitchen culinary team.`,
    has_company_logo: true,
    has_questions: true,
    telecommuting: false,
  },
  {
    id: 'real-emscad-2',
    title: 'Customer Success & Video Production Specialist',
    company_name: 'Cloud Video Platform Inc.',
    location: 'NZ, Auckland',
    department: 'Client Operations',
    salary_range: '$55,000 - $68,000 / yr',
    contact_email: 'careers@cloudvideoplatform.io',
    company_url: 'http://cloudvideoplatform.io',
    category: 'Real / Legitimate',
    verdict: 'LEGITIMATE (4/100 Risk)',
    why_explanation: 'EMSCAD #2: Established software company, thorough job description, structured support responsibilities, official corporate communication channels.',
    description: `We are a high-growth cloud video production platform operating globally. We are looking for an energetic, organized Customer Success Specialist to assist corporate customers with project kickoffs and video asset workflows.

Key Duties:
- Answer client questions regarding video turnaround times, render pipelines, and deliverables.
- Coordinate with freelance editors and corporate accounts to resolve production tickets.
- Maintain top-tier CSAT scores and support ticket response metrics.`,
    requirements: `Requirements:
- 1-2 years experience in SaaS customer support or agency account management.
- Excellent typing and written communication skills.
- Familiarity with Zendesk, Slack, and digital media production terminology.`,
    benefits: `Benefits:
- Modern office in Auckland CBD with hybrid flexibility.
- Ongoing professional development and tech gear allowance.`,
    has_company_logo: true,
    has_questions: true,
    telecommuting: false,
  },
  {
    id: 'real-emscad-4',
    title: 'Account Executive - Enterprise GIS Solutions',
    company_name: 'ESRI (Environmental Systems Research Institute)',
    location: 'US, DC, Washington',
    department: 'Federal & Public Sector',
    salary_range: '$110,000 - $140,000 / yr + OTE',
    contact_email: 'careers@esri.com',
    company_url: 'http://www.esri.com',
    category: 'Real / Legitimate',
    verdict: 'LEGITIMATE (2/100 Risk)',
    why_explanation: 'EMSCAD #4: Globally recognized GIS software corporation, thorough job specifications, corporate domain (@esri.com), company logo, standard enterprise interview stages.',
    description: `ESRI is seeking a talented Account Executive to drive adoption of our market-leading Geographic Information System (GIS) enterprise platforms across government and commercial institutions in the Washington DC region.

Responsibilities:
- Cultivate relationships with enterprise CIOs and spatial analytics directors.
- Lead strategic product demos, RFP responses, and multi-year software agreement renewals.
- Partner with solutions architects to solve critical geospatial challenges.`,
    requirements: `Requirements:
- 5+ years successful B2B enterprise software sales experience.
- Familiarity with geospatial data, mapping solutions, or cloud infrastructure.
- Bachelor's degree in Business, Geography, Computer Science or related field.`,
    benefits: `Benefits:
- Uncapped commission structure with aggressive accelerators.
- Comprehensive 401(k) matching, health and tuition reimbursement.`,
    has_company_logo: true,
    has_questions: true,
    telecommuting: false,
  },
]


export const MOCK_HISTORICAL_JOBS = [
  {
    id: 'JOB-9021',
    title: 'Global Crypto Payment Manager & Financial Task Specialist',
    company: 'Binance Wealth Asset Trust',
    location: 'Remote (Worldwide)',
    riskLevel: 'High Risk',
    riskScore: 96,
    fraudProbability: 0.96,
    createdAt: '2026-10-23T09:30:00Z',
    category: 'Crypto & Finance',
    keyFlags: ['Telegram/WhatsApp interview only', 'Money mule / Crypto forwarding', 'ProtonMail domain used for corporate hiring'],
    salary: '$8,500 - $14,000/mo',
    status: 'Flagged & Blocked',
  },
  {
    id: 'JOB-9020',
    title: 'Urgent Remote Data Entry Clerk & Billing Assistant',
    company: 'Apex Global Logistics LLC',
    location: 'Remote (US & Canada)',
    riskLevel: 'High Risk',
    riskScore: 84,
    fraudProbability: 0.84,
    createdAt: '2026-10-23T08:15:00Z',
    category: 'Data Entry',
    keyFlags: ['Upfront equipment check scam pattern', 'Free @gmail email for hiring', 'Exaggerated wage ($55/hr for data entry)'],
    salary: '$48 - $58/hr',
    status: 'Flagged & Blocked',
  },
  {
    id: 'JOB-9019',
    title: 'Staff Software Engineer - Cloud Architecture',
    company: 'Stripe Technologies Inc.',
    location: 'San Francisco, CA (Hybrid)',
    riskLevel: 'Safe',
    riskScore: 4,
    fraudProbability: 0.04,
    createdAt: '2026-10-22T17:42:00Z',
    category: 'Technology',
    keyFlags: ['Verified corporate domain & MX records', 'Standard market compensation', 'Comprehensive verifiable interview process'],
    salary: '$210k - $265k/yr',
    status: 'Verified Safe',
  },
  {
    id: 'JOB-9018',
    title: 'Executive Assistant to Managing Director',
    company: 'Vanguard Capital Partners',
    location: 'New York, NY',
    riskLevel: 'Safe',
    riskScore: 8,
    fraudProbability: 0.08,
    createdAt: '2026-10-22T14:10:00Z',
    category: 'Finance',
    keyFlags: ['Registered corporate entity', 'Standard corporate recruitment process'],
    salary: '$95,000 - $115,000/yr',
    status: 'Verified Safe',
  },
  {
    id: 'JOB-9017',
    title: 'Package Inspection & Reshipment Inspector',
    company: 'Speedy Express Dispatch LLC',
    location: 'Atlanta, GA (Remote)',
    riskLevel: 'High Risk',
    riskScore: 91,
    fraudProbability: 0.91,
    createdAt: '2026-10-22T11:05:00Z',
    category: 'Logistics',
    keyFlags: ['Reshipping fraud pattern (stolen merchandise)', 'Unlicensed home delivery redirect', 'No tax withholding W-4'],
    salary: '$3,800/mo',
    status: 'Flagged & Blocked',
  },
  {
    id: 'JOB-9016',
    title: 'Senior Product Marketing Manager',
    company: 'Datadog Inc.',
    location: 'Boston, MA (Hybrid)',
    riskLevel: 'Safe',
    riskScore: 6,
    fraudProbability: 0.06,
    createdAt: '2026-10-21T16:20:00Z',
    category: 'Marketing',
    keyFlags: ['Verified domain', 'Standard benefits breakdown', 'Transparent reporting structure'],
    salary: '$160k - $185k/yr',
    status: 'Verified Safe',
  },
  {
    id: 'JOB-9015',
    title: 'Online Mystery Shopper & Product Reviewer',
    company: 'Consumer Insights Panel UK',
    location: 'London, UK (Remote)',
    riskLevel: 'Suspicious',
    riskScore: 62,
    fraudProbability: 0.62,
    createdAt: '2026-10-21T12:00:00Z',
    category: 'Customer Support',
    keyFlags: ['Gift card purchase task mentioned', 'Generic non-corporate recruitment portal', 'Lack of company registration number'],
    salary: '£350 - £600/wk',
    status: 'Under Review',
  },
  {
    id: 'JOB-9014',
    title: 'AI Prompt Engineer & Data Labeler',
    company: 'Scale AI Corporation',
    location: 'San Francisco, CA',
    riskLevel: 'Safe',
    riskScore: 9,
    fraudProbability: 0.09,
    createdAt: '2026-10-20T19:40:00Z',
    category: 'Technology',
    keyFlags: ['Domain DNS matches official careers system', 'Coherent technical spec'],
    salary: '$110,000 - $140,000/yr',
    status: 'Verified Safe',
  },
  {
    id: 'JOB-9013',
    title: 'Virtual Healthcare Claims Billing Specialist',
    company: 'MedTrust Health Care LLC',
    location: 'Chicago, IL (Remote)',
    riskLevel: 'Suspicious',
    riskScore: 54,
    fraudProbability: 0.54,
    createdAt: '2026-10-20T10:15:00Z',
    category: 'Healthcare',
    keyFlags: ['HIPAA certification not required despite claims role', 'Inconsistent corporate registration info', 'Disposable Outlook email'],
    salary: '$32 - $38/hr',
    status: 'Under Review',
  },
  {
    id: 'JOB-9012',
    title: 'Lead Frontend Engineer (React/TypeScript)',
    company: 'Linear App',
    location: 'Remote (Worldwide)',
    riskLevel: 'Safe',
    riskScore: 3,
    fraudProbability: 0.03,
    createdAt: '2026-10-19T15:20:00Z',
    category: 'Technology',
    keyFlags: ['Verified corporate portal', 'Standard salary band', 'Thorough technical interview stages'],
    salary: '$170k - $210k/yr',
    status: 'Verified Safe',
  },
  {
    id: 'JOB-9011',
    title: 'Urgent Wire Transfer Officer & Payroll Assistant',
    company: 'Global Horizon Investment Group',
    location: 'Miami, FL',
    riskLevel: 'High Risk',
    riskScore: 94,
    fraudProbability: 0.94,
    createdAt: '2026-10-18T18:00:00Z',
    category: 'Finance',
    keyFlags: ['Personal bank account requirement', 'Urgent unvetted hiring', 'Off-platform encrypted chat interview'],
    salary: '$6,500/mo',
    status: 'Flagged & Blocked',
  },
  {
    id: 'JOB-9010',
    title: 'Customer Experience Associate (Bilingual)',
    company: 'Airbnb Inc.',
    location: 'Austin, TX',
    riskLevel: 'Safe',
    riskScore: 5,
    fraudProbability: 0.05,
    createdAt: '2026-10-18T11:30:00Z',
    category: 'Customer Support',
    keyFlags: ['Legitimate Greenhouse applicant tracking link', 'Verified benefits package'],
    salary: '$52,000 - $65,000/yr',
    status: 'Verified Safe',
  },
]

export const MOCK_TREND_DATA = [
  { month: 'May', totalScanned: 840, fakeDetected: 185, suspicious: 95 },
  { month: 'Jun', totalScanned: 1120, fakeDetected: 240, suspicious: 140 },
  { month: 'Jul', totalScanned: 1390, fakeDetected: 310, suspicious: 165 },
  { month: 'Aug', totalScanned: 1850, fakeDetected: 430, suspicious: 220 },
  { month: 'Sep', totalScanned: 2420, fakeDetected: 590, suspicious: 310 },
  { month: 'Oct', totalScanned: 3150, fakeDetected: 720, suspicious: 390 },
]

export const MOCK_INDUSTRY_DATA = [
  { industry: 'Data Entry & Clerical', total: 2450, fake: 1140, riskRate: 46.5 },
  { industry: 'Crypto & High-Yield', total: 1620, fake: 760, riskRate: 46.9 },
  { industry: 'Customer Care & Admin', total: 3200, fake: 890, riskRate: 27.8 },
  { industry: 'Software & Technology', total: 4210, fake: 380, riskRate: 9.0 },
  { industry: 'Healthcare & Nursing', total: 3412, fake: 240, riskRate: 7.0 },
]

export const MOCK_RED_FLAGS = [
  { flag: 'Unverified / Free Public Email Domain (@gmail, @proton, @yahoo)', count: 1845, percent: 54, severity: 'High' },
  { flag: 'Upfront Equipment Check / Cashier Reimbursement Scheme', count: 1420, percent: 41, severity: 'Critical' },
  { flag: 'Interview Directed Exclusively to Telegram / WhatsApp / Signal', count: 1290, percent: 38, severity: 'Critical' },
  { flag: 'Abnormal Salary-to-Skill Ratio (Entry level offered $60+/hr)', count: 1040, percent: 30, severity: 'Medium' },
  { flag: 'Vague Responsibilities & Absence of Official Registered Company Domain', count: 890, percent: 26, severity: 'Medium' },
  { flag: 'Request for Personal Bank Credentials / SSN Before Contract', count: 760, percent: 22, severity: 'Critical' },
]

export const MOCK_SEVERITY_DISTRIBUTION = [
  { name: 'Safe Postings', value: 64.7, color: '#10b981' },
  { name: 'Suspicious / Inconclusive', value: 12.4, color: '#f59e0b' },
  { name: 'Confirmed Fraudulent', value: 22.9, color: '#f43f5e' },
]

// Dynamic AI Analysis Engine simulation
export function analyzeJobMock(jobData) {
  const text = `${jobData.title || ''} ${jobData.company_name || ''} ${jobData.description || ''} ${jobData.requirements || ''} ${jobData.benefits || ''} ${jobData.contact_email || ''} ${jobData.salary_range || ''}`.toLowerCase()

  const detectedFlags = []
  let calculatedScore = 8 // base low risk

  // 1. Communication channels red flag
  if (text.includes('telegram') || text.includes('whatsapp') || text.includes('signal') || text.includes('@hr_') || text.includes('chat interview')) {
    calculatedScore += 38
    detectedFlags.push({
      id: 'flag-comm',
      title: 'Off-Platform Encrypted Chat Interview',
      severity: 'Critical',
      description: 'Hiring manager requests communication via Telegram, WhatsApp, or instant messaging without formal video or company email.',
    })
  }

  // 2. Equipment check scam pattern
  if (text.includes('check') || text.includes('equipment') || text.includes('cashier') || text.includes('vendor check') || text.includes('reimbursement check')) {
    calculatedScore += 32
    detectedFlags.push({
      id: 'flag-check',
      title: 'Upfront Equipment Check / Fake Check Scheme',
      severity: 'Critical',
      description: 'The employer states they will send a check to purchase home office hardware/software from a "certified vendor" — a textbook scam pattern.',
    })
  }

  // 3. Crypto / money forwarding pattern
  if (text.includes('crypto') || text.includes('bitcoin') || text.includes('usdt') || text.includes('atm') || text.includes('forwarding') || text.includes('client funds')) {
    calculatedScore += 36
    detectedFlags.push({
      id: 'flag-crypto',
      title: 'Money Mule / Illicit Crypto Transaction Routing',
      severity: 'Critical',
      description: 'Instructions to convert funds into cryptocurrency or send payments through personal accounts indicates illegal money laundering or financial fraud.',
    })
  }

  // 4. Free email domain for corporate hiring
  const email = (jobData.contact_email || '').toLowerCase()
  if (email.endsWith('@gmail.com') || email.endsWith('@yahoo.com') || email.endsWith('@hotmail.com') || email.endsWith('@protonmail.com') || email.endsWith('@outlook.com')) {
    calculatedScore += 24
    detectedFlags.push({
      id: 'flag-email',
      title: 'Unverified Free / Disposable Email Provider',
      severity: 'High',
      description: `Job contact uses free webmail (${email}) instead of a verified enterprise domain (@company.com).`,
    })
  }

  // 5. Unrealistic compensation for low skill
  if (text.includes('no experience') && (text.includes('$45') || text.includes('$50') || text.includes('$55') || text.includes('$60') || text.includes('$8,000') || text.includes('$10,000') || text.includes('$14,000'))) {
    calculatedScore += 22
    detectedFlags.push({
      id: 'flag-salary',
      title: 'Severe Compensation-Skill Disparity',
      severity: 'Medium',
      description: 'Offered compensation far exceeds market benchmarks for entry-level tasks requiring no experience, often used as bait.',
    })
  }

  // 6. Urgency and instant hire without interview
  if (text.includes('immediate hire') || text.includes('urgent') || text.includes('start today') || text.includes('no interview') || text.includes('instant hire')) {
    calculatedScore += 14
    detectedFlags.push({
      id: 'flag-urgency',
      title: 'High-Pressure Urgency & Instant Hiring',
      severity: 'Medium',
      description: 'Pressuring candidates to act immediately without formal background checks or proper interviews is typical of scam operations.',
    })
  }

  // 7. Requesting sensitive info / ID upfront
  if (text.includes('photo id') || text.includes('selfie holding id') || text.includes('checking account') || text.includes('banking info') || text.includes('ssn')) {
    calculatedScore += 28
    detectedFlags.push({
      id: 'flag-id',
      title: 'Premature Personal Identity / Banking Collection',
      severity: 'Critical',
      description: 'Requesting government ID selfies or bank account credentials before a formal written offer and background check poses identity theft risks.',
    })
  }

  // 8. Positive signals (verified corporate signals)
  if (text.includes('stripe') || text.includes('google') || text.includes('datadog') || text.includes('scale ai') || text.includes('linear')) {
    if (detectedFlags.length === 0) {
      calculatedScore = Math.min(calculatedScore, 6)
    }
  }

  // Clamp risk score
  const finalScore = Math.min(Math.max(calculatedScore, 4), 98)

  let riskLevel = 'Safe'
  if (finalScore >= 70) {
    riskLevel = 'High Risk'
  } else if (finalScore >= 35) {
    riskLevel = 'Suspicious'
  }

  const fraudProbability = (finalScore / 100).toFixed(2)

  // Radar metrics
  const radarBreakdown = [
    { metric: 'Text Linguistic Coherence', score: finalScore > 70 ? 42 : finalScore > 35 ? 68 : 96 },
    { metric: 'Company Domain Trust', score: finalScore > 70 ? 15 : finalScore > 35 ? 45 : 98 },
    { metric: 'Salary Market Alignment', score: finalScore > 70 ? 25 : finalScore > 35 ? 58 : 92 },
    { metric: 'Interview Process Legitimacy', score: finalScore > 70 ? 18 : finalScore > 35 ? 52 : 95 },
    { metric: 'Contact Channel Credibility', score: finalScore > 70 ? 12 : finalScore > 35 ? 48 : 97 },
  ]

  // Recommendations
  const recommendations = []
  if (riskLevel === 'High Risk') {
    recommendations.push('Do NOT send any funds, cash any checks, or purchase equipment through third-party vendors.')
    recommendations.push('Do NOT share government photo IDs, selfies, or banking details over unverified chat apps.')
    recommendations.push('Report this posting to the job board and local trade fraud enforcement.')
  } else if (riskLevel === 'Suspicious') {
    recommendations.push('Verify the employer by independently looking up their official corporate website and contacting their HR office directly.')
    recommendations.push('Demand a face-to-face video interview through an enterprise platform (Zoom, Teams, Google Meet) with company email invitations.')
    recommendations.push('Be cautious of any request for pre-employment fees or background check processing fees.')
  } else {
    recommendations.push('Job posting displays healthy corporate indicators, verified domain patterns, and realistic salary bands.')
    recommendations.push('Follow standard application protocols through the verified company portal or LinkedIn.')
  }

  return {
    id: `JOB-${Math.floor(1000 + Math.random() * 9000)}`,
    title: jobData.title || 'Untitled Job Analysis',
    company: jobData.company_name || 'Unspecified Company',
    location: jobData.location || 'Remote',
    salary: jobData.salary_range || 'Not specified',
    riskScore: finalScore,
    riskLevel,
    fraudProbability: parseFloat(fraudProbability),
    createdAt: new Date().toISOString(),
    status: riskLevel === 'High Risk' ? 'Flagged & Blocked' : riskLevel === 'Suspicious' ? 'Under Review' : 'Verified Safe',
    category: jobData.department || 'General',
    flags: detectedFlags,
    radarBreakdown,
    recommendations,
    modelMetadata: {
      engine: 'NLP-Ensemble-v1.4',
      tokenCount: text.split(/\s+/).length,
      latencyMs: Math.floor(110 + Math.random() * 60),
      confidence: (94 + Math.random() * 5).toFixed(1) + '%',
    },
  }
}
