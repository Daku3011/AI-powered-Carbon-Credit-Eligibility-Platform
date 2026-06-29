# Original User Request

## Initial Request — 2026-06-29T20:19:55+05:30

An AI-powered Carbon Intelligence Platform that helps organizations (MSMEs, factories, schools, farms, housing societies) transition from carbon measurement to monetization. The system supports industry-specific profiles, smart document analysis, eligibility scoring, carbon reduction roadmaps, a project marketplace, comparative benchmarking, and an AI consultant chatbot utilizing a knowledge base.

Working directory: /home/dwarkeshramani/Projects/ai_carbon_credits
Integrity mode: development

## Requirements

### R1. Tailored Industry Profiles & Smart Questionnaire
Provide custom data capture flows tailored to specific industry sectors (e.g. Manufacturing, Textile, Schools, Farms, Housing Societies). The questionnaire must capture energy, fuel, waste, and operational metrics.

### R2. AI Document Analysis & OCR
Allow users to upload utility bills, fuel invoices, or energy sheets (PDF, PNG, JPG). Integrate document processing/OCR (leveraging the Gemini API) to extract consumption figures, costs, and fuels automatically to prepopulate the questionnaire.

### R3. Carbon Calculator & AI Eligibility Scoring
Calculate scope 1 and scope 2 emissions, and evaluate an AI Eligibility Score (0-100 readiness, emissions, reduction potential percentage, carbon credit potential, financial revenue projection, and confidence score).

### R4. Carbon Roadmap & Project Marketplace
- **Marketplace**: Browse pre-defined decarbonization projects (e.g., Solar, Biogas, EV transition, Waste recovery) showing cost, ROI, payback, and carbon credit potential.
- **Roadmap**: Generate a multi-year actionable implementation plan (Year 1, 2, 3+) detailing steps, investment, savings, and carbon credits earned.

### R5. Interactive Benchmarking Dashboard
A visual dashboard comparing user emissions and energy metrics against regional or industry averages (e.g. percentage better/worse, carbon intensity comparisons) with dynamic charts.

### R6. AI Carbon Consultant & Knowledge Base Chatbot
An AI chatbot utilizing the Gemini API that answers queries regarding registration processes, carbon methodologies, and Indian policies using an indexed reference knowledge base of carbon regulations.

### R7. PDF & Excel Export Reports
Generate professional, comprehensive downloadable PDF and Excel reports containing input summaries, emission analytics, eligibility score metrics, and the generated carbon reduction roadmap.

## Acceptance Criteria

### Data Capture & OCR
- [ ] Uploading sample electricity/fuel bills extracts correct units and costs via OCR.
- [ ] Users can select distinct industry profiles changing the metric questions asked.

### Calculations & Score
- [ ] Emits accurate scope 1/scope 2 metrics based on industry standard factors.
- [ ] Produces a multi-metric eligibility scorecard displaying the readiness score, credit potential, and projected financial yields.

### Projects & Planning
- [ ] The system populates a multi-year actionable roadmap showing specific annual recommendations and credit milestones.
- [ ] Users can browse a marketplace of project ideas and view payback/ROI details.

### Benchmarking & Chatbot
- [ ] Chatbot answers domain-specific carbon market questions correctly referencing regulations.
- [ ] Visual charts compare current user footprint against preset industry averages.

### Reports
- [ ] System exports a valid PDF and Excel containing calculated emissions, eligibility score, and multi-year roadmap.
