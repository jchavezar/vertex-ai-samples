import os
import json
from jinja2 import Template
from weasyprint import HTML, CSS

Internal_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @page {
            size: A4;
            margin: 20mm;
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-family: sans-serif;
                font-size: 8pt;
                color: #888;
            }
        }
        
        body {
            font-family: serif;
            color: #000;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        .header {
            border-bottom: 4px solid #000;
            padding-bottom: 20px;
            margin-bottom: 40px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }

        .header-left h1 {
            font-size: 48px;
            font-weight: 900;
            margin: 0;
            letter-spacing: -1.5px;
            font-family: sans-serif;
            line-height: 1;
        }

        .header-left h2 {
            font-size: 20px;
            font-weight: 500;
            color: #444;
            margin: 8px 0 0 0;
            font-family: sans-serif;
        }

        .header-right {
            text-align: right;
            float: right;
        }

        .header-right .tag {
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            color: #666;
            font-family: sans-serif;
        }

        .header-right .brand {
            font-weight: 800;
            font-size: 14px;
            font-family: sans-serif;
            margin: 4px 0;
        }

        .report-content {
            display: block;
            clear: both;
        }

        .section {
            margin-bottom: 30px;
            page-break-inside: avoid;
        }

        .section-title {
            font-size: 14px;
            font-weight: 900;
            text-transform: uppercase;
            color: #111;
            margin-bottom: 16px;
            font-family: sans-serif;
            border-left: 4px solid #004b87;
            padding-left: 12px;
            letter-spacing: 0.5px;
        }

        .component-text {
            font-size: 15px;
            color: #333;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-family: sans-serif;
            font-size: 13px;
        }

        th {
            background: #f8f9fa;
            border-bottom: 2px solid #000;
            padding: 10px;
            text-align: left;
            font-weight: 800;
        }

        td {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }

        .hero {
            text-align: center;
            margin: 60px 0;
        }

        .hero h1 {
            font-size: 36px;
            font-weight: 900;
        }

        .hero p {
            font-size: 18px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-right">
            <div class="tag">Equity Research</div>
            <div class="brand">FactSet Stock Terminal AI</div>
            <div class="date">{{ date }}</div>
        </div>
        <div class="header-left">
            <h1>{{ ticker }}</h1>
            <h2>{{ title }}</h2>
        </div>
    </div>

    <div class="report-content">
        {% for component in components %}
            <div class="section">
                {% if component.type == 'hero' %}
                    <div class="hero">
                        <h1>{{ component.title }}</h1>
                        <p>{{ component.subtitle }}</p>
                    </div>
                {% elif component.type == 'text' %}
                    {% if component.title %}
                        <div class="section-title">{{ component.title }}</div>
                    {% endif %}
                    <div class="component-text">
                        {{ component.html_content | safe }}
                    </div>
                {% elif component.type == 'chart' %}
                    <div class="section-title">{{ component.title }} (Data Visualization)</div>
                    <div class="data-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% if component.data is mapping %}
                                    {% for key, val in component.data.items() %}
                                        <tr>
                                            <td>{{ key }}</td>
                                            <td>{{ val }}</td>
                                        </tr>
                                    {% endfor %}
                                {% elif component.data is iterable %}
                                    {% for item in component.data %}
                                        <tr>
                                            <td>{{ item.label or item.date or 'N/A' }}</td>
                                            <td>{{ item.value or item.close or 'N/A' }}</td>
                                        </tr>
                                    {% endfor %}
                                {% endif %}
                            </tbody>
                        </table>
                    </div>
                {% endif %}
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def render_report(report_data, output_path):
    import markdown
    from markdown.extensions.tables import TableExtension

    processed_components = []
    for comp in report_data.get("components", []):
        new_comp = comp.copy()
        if comp.get("type") == "text":
            new_comp["html_content"] = markdown.markdown(
                comp.get("content", ""), 
                extensions=[TableExtension()]
            )
        processed_components.append(new_comp)

    template = Template(Internal_TEMPLATE)
    html_out = template.render(
        ticker=report_data.get("ticker", "UNKNOWN"),
        title=report_data.get("title", "Investment Report"),
        date=report_data.get("date", "March 2026"),
        components=processed_components
    )

    HTML(string=html_out).write_pdf(output_path)
    return output_path

if __name__ == "__main__":
    test_json = {
        "ticker": "AAPL",
        "title": "Quarterly Update",
        "date": "March 2026",
        "components": [
            {
                "type": "hero",
                "title": "APPLE INC PRIMER",
                "subtitle": "Fiscal Year 2026 Analysis"
            },
            {
                "type": "text",
                "title": "Executive Summary",
                "content": "Apple is doing **great** in FY2026. Revenues are up across all segments.\n\n| Segment | Revenue |\n|---|---|\n| iPhone | $50B |\n| Services | $20B |"
            },
            {
                "type": "chart",
                "title": "Historical Sales",
                "data": [
                    {"label": "2023", "value": 100},
                    {"label": "2024", "value": 120},
                    {"label": "2025", "value": 150}
                ]
            }
        ]
    }
    render_report(test_json, "test_internal_report.pdf")
    print("Test report saved to test_internal_report.pdf")
