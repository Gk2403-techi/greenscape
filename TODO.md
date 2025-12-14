# GreenScape AI Enhancement TODO

## 0. Role Definitions
- [x] Define clear roles at the start: Homeowner (B2C), Landscaping Business (B2B), Admin
- [x] Update form UI to reflect new roles with descriptions
- [x] Adjust backend logic for role-based ratios (Landscaping Business uses Architect ratios)

## 1. Plant Database and Seasonal Recommendations
- [x] Create plants.json with plant data (names, seasons, zones, maintenance)
- [x] Add zip code to season mapping logic
- [x] Update calculate_plan_logic to select plants based on season/soil
- [x] Update results UI to display recommended plants

## 2. Maintenance Schedules
- [x] Extend plant data with maintenance tasks
- [x] Add maintenance schedule generation in calculate_plan_logic
- [x] Update results UI to show maintenance calendar

## 3. Enhanced User Inputs for AI-Powered Landscape Design
- [x] Add zip code input for climate/weather determination
- [x] Add climate select dropdown (Temperate, Subtropical, Continental, Arid, Mediterranean)
- [x] Add maintenance level select (Low, Medium, High)
- [x] Expose style as select dropdown (Modern, Traditional, Rustic, Minimalist)
- [x] Expose terrain as select dropdown (Flat, Hilly, Sloped)
- [x] Expose usage as select dropdown (Family, Entertainment, Relaxation)
- [x] Expose privacy as select dropdown (Semi-Private, Private, Open)
- [x] Expose water_feature as select dropdown (None, Swimming Pool, Koi Pond, Fountain)
- [x] Update calculate_plan_logic to use climate and maintenance level for plant recommendations
- [x] Update form UI to display new inputs in organized grid layout

## 4. Bulk Design Generation
- [ ] Add /bulk_generate route
- [ ] Modify form for bulk mode option
- [ ] Generate and display multiple plan variations

## 5. Appointment Scheduling
- [ ] Add /schedule route
- [ ] Create scheduling UI in template
- [ ] Implement in-memory appointment storage

## Testing & Followup
- [ ] Test all features
- [ ] Update requirements.txt if needed
- [ ] Run app locally
