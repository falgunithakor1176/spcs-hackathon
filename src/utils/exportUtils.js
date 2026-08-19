/**
 * exportUtils.js — CSV and PDF export utilities
 * Pure JS — no external libraries required.
 */

/**
 * Export an array of objects to a CSV file download.
 * @param {Object[]} data    - Array of flat objects
 * @param {string}   filename - e.g. 'crimes_export.csv'
 */
export function exportToCSV(data, filename = 'export.csv') {
  if (!data || data.length === 0) {
    alert('No data to export.');
    return;
  }
  const headers = Object.keys(data[0]);
  const csvRows = [
    headers.join(','),
    ...data.map(row =>
      headers.map(h => {
        const val = row[h] === null || row[h] === undefined ? '' : String(row[h]);
        // Escape double-quotes and wrap in quotes if contains comma/newline
        return val.includes(',') || val.includes('"') || val.includes('\n')
          ? `"${val.replace(/"/g, '""')}"`
          : val;
      }).join(',')
    ),
  ];
  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url  = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href     = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Export a simple table to a print-ready PDF via window.print().
 * @param {string}   title   - Report title
 * @param {string[]} headers - Column headers
 * @param {Array[]}  rows    - 2D array of row data
 */
export function exportToPDF(title, headers, rows) {
  const tableRows = rows.map(row =>
    `<tr>${row.map(cell => `<td>${cell ?? ''}</td>`).join('')}</tr>`
  ).join('');

  const html = `
    <html>
    <head>
      <title>${title}</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 24px; color: #111; }
        h2 { font-size: 18px; margin-bottom: 4px; }
        .meta { font-size: 11px; color: #666; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th { background: #0f1e3c; color: #fff; padding: 6px 8px; text-align: left; }
        td { padding: 5px 8px; border-bottom: 1px solid #e0e0e0; }
        tr:nth-child(even) td { background: #f9f9f9; }
        @media print { body { padding: 0; } }
      </style>
    </head>
    <body>
      <h2>SPCS — ${title}</h2>
      <div class="meta">Generated: ${new Date().toLocaleString()} | Smart Policing Command System</div>
      <table>
        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
        <tbody>${tableRows}</tbody>
      </table>
    </body>
    </html>
  `;

  const win = window.open('', '_blank');
  win.document.write(html);
  win.document.close();
  win.print();
}

/**
 * Helper: flatten crimes array for CSV export.
 */
export function crimesToCSV(crimes) {
  return crimes.map(c => ({
    crime_id:    c.crime_id,
    crime_type:  c.crime_type,
    area:        c.area,
    zone:        c.zone,
    severity:    c.severity,
    status:      c.status,
    timestamp:   c.timestamp,
    fir_number:  c.fir_number,
    latitude:    c.latitude,
    longitude:   c.longitude,
  }));
}

/**
 * Helper: flatten area intelligence for CSV export.
 */
export function intelligenceToCSV(rows) {
  return rows.map(r => ({
    area:                 r.area,
    zone:                 r.zone,
    combined_risk:        r.combined_risk,
    combined_risk_score:  r.combined_risk_score,
    physical_risk:        r.physical_risk,
    predicted_count:      r.predicted_count,
    cyber_risk:           r.cyber_risk,
    hotspot_risk:         r.hotspot_risk,
    patrol_priority:      r.patrol_priority,
    forecast_period:      `${r.forecast_year}-${String(r.forecast_month).padStart(2,'0')}`,
  }));
}
