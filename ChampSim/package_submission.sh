#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

SUBMISSION_DIR="Group23_Project3"

echo "Creating submission directory: $SUBMISSION_DIR"
mkdir -p "$SUBMISSION_DIR"

echo "Copying configuration files..."
cp *_config.json "$SUBMISSION_DIR/"

echo "Copying automation and analysis scripts..."
cp run_*.sh "$SUBMISSION_DIR/"
cp parse_results.py plot_results.py plot_mpki.py plot_acc_cov.py plot_dram.py analyze_accesses.py "$SUBMISSION_DIR/"

echo "Copying data, access samples, and plots..."
cp simulation_summary.csv sample_fotonik3d.csv sample_bfscc.csv sample_xalancbmk.csv "$SUBMISSION_DIR/"
cp -r plots "$SUBMISSION_DIR/"

echo "Copying modified source code (Deliverable 3)..."
mkdir -p "$SUBMISSION_DIR/prefetcher/no"
cp prefetcher/no/no.cc "$SUBMISSION_DIR/prefetcher/no/"

echo "Copying README documentation..."
cp README.md "$SUBMISSION_DIR/"

echo "Fetching PDF reports from Downloads..."

# Check and move the Overleaf Report
if [ -f "$HOME/Downloads/CA_Project_Report.pdf" ]; then
    mv "$HOME/Downloads/CA_Project_Report.pdf" "$SUBMISSION_DIR/${SUBMISSION_DIR}_Report.pdf"
    echo "  -> Successfully moved CA_Project_Report.pdf"
else
    echo "  -> [WARNING]: CA_Project_Report.pdf not found in Downloads. Please drop it into $SUBMISSION_DIR manually."
fi

# Check and move the Overleaf Presentation
if [ -f "$HOME/Downloads/CA_Project_PPT.pdf" ]; then
    mv "$HOME/Downloads/CA_Project_PPT.pdf" "$SUBMISSION_DIR/${SUBMISSION_DIR}_Presentation.pdf"
    echo "  -> Successfully moved CA_Project_PPT.pdf"
else
    echo "  -> [WARNING]: CA_Project_PPT.pdf not found in Downloads. Please drop it into $SUBMISSION_DIR manually."
fi

echo "Packaging the final ZIP archive..."
zip -r "${SUBMISSION_DIR}.zip" "$SUBMISSION_DIR"

echo ""
echo "====================================================="
echo "Success! ${SUBMISSION_DIR}.zip is ready for upload."
echo "====================================================="
