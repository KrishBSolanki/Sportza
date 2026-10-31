# Sportza Performance Lab

SPORTZA — Frontend Visual Theme Redesign Prompt
A simple, classy, professional light theme for a sports-science DSC project
Redesign the existing SPORTZA React frontend with a distinctive, restrained, premium light-only visual theme appropriate for a university sports-science analytics and athlete-performance research project.

This is a visual design and frontend styling task. Do not redesign the backend, data model, API contracts, machine-learning logic, prediction logic, or product scope. Preserve all currently working functionality and connect every existing screen to the same data and actions it uses today.

1. Design direction
   Create the feeling of a carefully designed sports-science platform used by coaches, performance analysts and researchers—not a generic AI-generated SaaS dashboard.

The visual identity should be:

- Calm, confident, clean and academic, with a subtle sporting character.
- Light, bright and comfortable for long periods of analysis.
- Editorial rather than decorative: strong hierarchy, good spacing and purposeful alignment.
- Data-first: charts, trends and athlete decisions should receive attention before containers and decoration.
- Consistent across every page, with the same typography, spacing, colors, controls and chart treatment.
  Think of a premium sports performance report translated into a modern web application: understated, precise and easy to understand.

2. Color system — light theme only
   Use one coherent light palette throughout the application. Do not add dark mode, dark theme, theme switching, or dark dashboard variants.

Suggested design tokens:

- Main page background: warm off-white #F6F7F4
- Main content surface: white #FFFFFF
- Secondary surface: soft neutral #EEF1ED
- Primary text: deep charcoal #202923
- Secondary text: muted slate #65716A
- Subtle borders: soft grey-green #DCE3DC
- Primary brand accent: deep forest green #27634B
- Secondary accent: muted sage #8DA996
- Highlight accent: restrained warm amber #C58A3A
- Negative/alert color: muted brick red #B95750
- Informational color: calm blue-grey #58778A
  Use the green accent for primary actions, active navigation and meaningful positive/selected states. Use amber and red only when the data calls for attention. Do not color every component.

Avoid:

- Black or near-black full-page backgrounds.
- Neon green, electric blue, purple gradients or rainbow accents.
- Glassmorphism, glowing borders, blurred backgrounds or gradient blobs.
- Heavy shadows, decorative color bands and excessive rounded cards.
  Create CSS variables/design tokens so the palette can be adjusted in one place.

3. Typography
   Use a clean, highly readable typography system:

- Prefer Inter, Source Sans 3, or a reliable system sans-serif fallback.
- Use restrained, medium-weight page headings; avoid oversized marketing-style hero titles.
- Use clear section headings and compact but readable chart labels.
- Use tabular numerals for measurements, dates, percentages and KPI values.
- Keep helper text visibly secondary without making it tiny or low contrast.
- Avoid mixing multiple unrelated font families.
  The application should read like a professional analytical tool, not a promotional landing page.

4. Layout and navigation
   Establish a consistent application shell:

- A slim, quiet left navigation rail/sidebar with a clear active state.
- A clean top area for page title, short context and essential page-level actions.
- A centered content region with a sensible maximum width and consistent margins.
- Use whitespace and alignment to organize content instead of enclosing every section in a card.
- Keep page layouts consistent while allowing each module to prioritize its own content.
- Ensure responsive behavior for laptop, tablet and mobile widths.
  Navigation should be simple and text-led. Use small, consistent icons only where they improve recognition. Do not use emojis as interface icons. Avoid oversized navigation blocks and decorative sidebars.

5. Components and visual treatment
   Apply one shared component system to:

- Page headers and section headers
- Sidebar and active navigation
- Primary, secondary and text buttons
- Inputs, selects, date pickers and filters
- KPI summaries
- Tables and expandable detail rows
- Status indicators and alerts
- Tabs and segmented controls
- Tooltips, empty states, loading states and error states
  Component rules:
- Prefer flat surfaces with subtle borders over floating cards.
- Use modest corner radii consistently; do not make every element a pill.
- Use shadows sparingly, only where separation genuinely helps.
- Give important numbers visual emphasis without turning every metric into a large tile.
- Use concise labels and plain language.
- Keep buttons compact, calm and consistent.
- Make tables easy to scan with aligned numeric columns, subtle row separators and clear hover states.
- Use badges only for meaningful statuses, not as decoration.

6. Charts and data visualization
   Charts are central to SPORTZA. Give them a coherent, publication-quality visual language.

Use:

- White chart plotting areas or transparent surfaces that blend naturally with the page.
- Minimal gridlines in a very light neutral grey.
- Dark, readable axis labels and clear units.
- A restrained palette built around forest green, sage, slate blue, muted amber and brick red.
- Consistent colors for the same metric across every page.
- Clear legends placed near the chart without covering the data.
- Sensible date ticks and readable tick labels.
- Tooltips that explain the metric, value, date and unit in plain language.
- Adequate chart height and spacing; avoid cramped or excessively tall charts.
  Choose the most suitable chart type for the question:
- Time trends: line charts, with a light contextual reference or baseline when meaningful.
- Workload distributions: box plots, histograms or clearly labeled bars.
- Correlation: annotated heatmap using a balanced diverging palette centered at zero.
- Injury locations/severity: simple heatmap or horizontal bars with a clear severity legend.
- Position comparisons: grouped or faceted plots that allow fair comparison.
- Actual vs predicted: scatter plot with a clear reference line and readable error context.
- Model evaluation: compact metric comparison and appropriate diagnostic charts.
  Do not add charts just to fill space. Every chart must answer a specific analytical question and have a descriptive title and a one-sentence explanation of what the viewer should notice. Never imply correlation is causation.

7. Apply the theme to the existing SPORTZA sections
   Keep the current sections and their functionality. Restyle them consistently:
   Overview
   A clear summary of the current dataset and athlete/team state. Use a restrained KPI row, one or two high-value trends, and a concise insight area. Do not create a wall of statistic cards.
   Athletes
   Make athlete selection, profile context and longitudinal trends easy to scan. Group related wellness and workload metrics logically. Do not display every variable as a separate oversized chart.
   Recovery Planner / Readiness
   Prioritize the current readiness context, recent changes and the evidence behind any suggestion. Make recovery guidance visually distinct but restrained. Show the factors contributing to a recommendation. Keep non-medical limitations clear and readable.
   Training Performance / Workload
   Present workload trends, session distribution and training metrics with clear units and consistent colors. Explain sRPE, acute/chronic load and other technical metrics briefly where needed.
   Injury Research
   Use clear severity encoding, a readable body-location summary and a timeline or distribution view. Clearly distinguish self-reported pain/injury notifications from clinical diagnoses.
   Performance Forecast
   Make forecast horizon, actual values, predicted values and uncertainty/limitations understandable. Use simple actual-versus-predicted visualizations and avoid exaggerated prediction badges.
   Team / Position Analysis
   Use clean comparative charts with consistent position labels, readable legends and fair scales. Avoid decorative panels and redundant charts.
   Correlation Lab
   Use a readable correlation heatmap with a balanced diverging scale centered at zero. Include a short explanation of strong positive and negative associations and a reminder that correlation does not establish causality.
   Data Models / Model Evaluation
   Use a compact, professional layout for model selection, validation methodology, baseline comparison and diagnostic charts. Show genuine model status and metrics only. Keep technical details available without overwhelming the main view.
8. Writing and microcopy
   Use direct, plain and professional language:

- Explain technical sports-science terms briefly.
- Prefer “Recent workload increased” over vague AI-style insight statements.
- Prefer “Readiness is lower than this athlete’s recent baseline” over unsupported claims about health.
- Do not use phrases such as “AI-powered next-generation intelligence”, “revolutionary insights” or generic marketing copy.
- Do not invent insights, explanations, dataset counts or model confidence values.
- Keep the wording concise and specific to the actual data displayed.

9. Implementation constraints

- Inspect the existing React project and identify its current styling system before editing.
- Reuse the current component framework and chart library where possible.
- Create shared theme variables and reusable style primitives rather than styling every page independently.
- Avoid adding a new UI library unless there is a clear technical need.
- Do not rewrite working API calls, services, state management, Python backend code, ML pipelines or data processing.
- Preserve all routes, filters, interactions, forms, charts and page functionality.
- Do not replace real API data with static examples or mock data.
- Do not remove useful source attribution or required non-medical disclaimers; make them visually quieter and place them where appropriate.
- Remove decorative clutter, redundant labels and repeated explanatory banners where they do not add user value.
- Ensure keyboard focus, sufficient color contrast, readable font sizes and accessible chart labels.
- Do not introduce a dark theme or a theme selector.

10. Quality checks and definition of done
    After applying the theme:
1. Run the frontend type check, lint and production build using the project's existing scripts.
1. Open every existing route and check that the theme is consistent.
1. Verify charts remain readable and interactive.
1. Verify tables, filters, buttons, forms, tooltips and navigation still work.
1. Verify loading, empty and error states use the same visual system.
1. Test common laptop and mobile viewport sizes.
1. Check for horizontal overflow, clipped labels, unreadable text, inconsistent spacing and layout shifts.
1. Confirm no API, backend or ML functionality has been broken by the redesign.
   The final result should be a cohesive, refined, light-only SPORTZA interface: understated, credible, readable and purpose-built for sports performance research.

Do not provide only a design proposal or screenshots. Implement the theme in the existing codebase and report the files changed and checks completed.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/ae7f6b0f-4084-4e62-83e5-81f06f6c91f9).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
