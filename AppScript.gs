function onEdit(e) {
  var sheet = e.source.getActiveSheet();
  var range = e.range;

  // Check if the edited cell is within your data range
  if (range.getColumn() <= 3) {
    // Change this value based on your actual data columns
    var row = range.getRow();
    var timestampColumn = 4; // Column D (change if needed)
    var timestampCell = sheet.getRange(row, timestampColumn);

    // Update the timestamp in MySQL format
    var now = new Date();
    var formattedTimestamp = Utilities.formatDate(
      now,
      Session.getScriptTimeZone(),
      "yyyy-MM-dd HH:mm:ss"
    );
    timestampCell.setValue(formattedTimestamp);
  }
}
