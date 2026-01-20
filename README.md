## Image Enhancement TODO

### Enhance 3D Render Prompt
- [x] Update render_prompt in calculate_plan_logic to include selected plants, lighting, irrigation systems, pathways, privacy features, dimensions, soil, climate, maintenance level
- [x] Make it highly detailed photorealistic with descriptive keywords

### Enhance 2D Blueprint Prompt
- [x] Update blueprint_prompt in calculate_plan_logic to include plants, lighting, irrigation, pathways, privacy elements, dimensions, labels, scale
- [x] Make it professional technical drawing with high contrast

### Increase Image Resolution
- [x] Change Pollinations resolution from 1280x720 to 1920x1080 in generate_image_url

### Test Enhancements
- [x] Test image generation to verify enhanced detail and equipment in outputs
- [x] Check for any errors in prompt building or image saving


## Enhancement TODO List

### PDF Export
- [x] Add reportlab to requirements.txt
- [x] Implement PDF generation function in main.py
- [x] Add /api/export_pdf endpoint
- [x] Add PDF export button to UI

### Database Persistence
- [x] Add SQLAlchemy and alembic to requirements.txt
- [x] Create database models for plans
- [x] Add database initialization in main.py
- [x] Add /api/save_plan and /api/load_plans endpoints
- [x] Implement save/load functionality

### UI/UX Improvements
- [x] Add save/load buttons to results section
- [x] Add plan gallery/modal for loading saved plans
- [x] Improve loading animations and states
- [x] Add plan comparison feature
- [x] Enhance mobile responsiveness

### Testing & Finalization
- [x] Test PDF generation
- [x] Test database operations
- [x] Update main TODO.md
- [x] Ensure compatibility with existing features
