@app.route('/static/evidence/<path:filename>')
def serve_evidence(filename):
    return send_from_directory(app.config['EVIDENCE_DIR'], filename)
