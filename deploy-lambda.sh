#!/bin/bash
# Enhanced AWS Lambda Deployment Package Creator
# No external dependencies version (no bc required)
set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

echo "========================================="
echo "AWS Lambda Deployment Package Creator"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
PACKAGE_DIR="${BACKEND_DIR}/package"
ZIP_FILE="${BACKEND_DIR}/lambda-deployment.zip"
MAX_LAMBDA_SIZE=$((250 * 1024 * 1024))  # 250 MB unzipped limit
MAX_ZIP_SIZE=$((50 * 1024 * 1024))       # 50 MB zipped limit (direct upload)

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to convert bytes to human readable (no bc needed)
bytes_to_human() {
    local bytes=$1
    if [ "$bytes" -ge 1073741824 ]; then
        echo "$((bytes / 1073741824))GB"
    elif [ "$bytes" -ge 1048576 ]; then
        echo "$((bytes / 1048576))MB"
    elif [ "$bytes" -ge 1024 ]; then
        echo "$((bytes / 1024))KB"
    else
        echo "${bytes}B"
    fi
}

# Function to get file size (cross-platform)
get_file_size() {
    local file=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        stat -f%z "$file" 2>/dev/null
    else
        # Linux
        stat -c%s "$file" 2>/dev/null
    fi
}

# Function to cleanup on error
cleanup_on_error() {
    print_error "An error occurred. Cleaning up..."
    rm -rf "$PACKAGE_DIR"
    exit 1
}

# Set trap for cleanup on error
trap cleanup_on_error ERR

# ============================================
# VALIDATION CHECKS
# ============================================

echo -e "${YELLOW}Running pre-deployment checks...${NC}"

# Check if we're in the correct directory
if [ ! -f "${BACKEND_DIR}/main.py" ]; then
    print_error "backend/main.py not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi
print_success "Found main.py"

# Check if requirements.txt exists
if [ ! -f "${BACKEND_DIR}/requirements.txt" ]; then
    print_error "backend/requirements.txt not found!"
    exit 1
fi
print_success "Found requirements.txt"

# Check for required directories
REQUIRED_DIRS=("${BACKEND_DIR}/agents" "${BACKEND_DIR}/config" "${BACKEND_DIR}/models")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        print_warning "Directory not found: $dir (will continue without it)"
    else
        print_success "Found directory: $dir"
    fi
done

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed!"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION detected"

# Check if pip is installed
if ! command_exists pip3 && ! command_exists pip; then
    print_error "pip is not installed!"
    exit 1
fi
print_success "pip detected"

# Check if zip is installed
if ! command_exists zip; then
    print_error "zip utility is not installed!"
    echo "Install it with: sudo apt-get install zip (Ubuntu) or brew install zip (Mac)"
    exit 1
fi
print_success "zip utility detected"

# Optional: Check if AWS CLI is installed (for automatic upload)
AWS_CLI_AVAILABLE=false
if command_exists aws; then
    AWS_CLI_AVAILABLE=true
    print_success "AWS CLI detected (automatic upload available)"
else
    print_warning "AWS CLI not detected (manual upload required)"
fi

echo ""

# ============================================
# CLEANUP OLD PACKAGE
# ============================================

echo -e "${YELLOW}Step 1: Cleaning up old package...${NC}"
rm -rf "$PACKAGE_DIR"
rm -f "$ZIP_FILE"
print_success "Cleanup complete"
echo ""

# ============================================
# CREATE PACKAGE DIRECTORY
# ============================================

echo -e "${YELLOW}Step 2: Creating package directory...${NC}"
mkdir -p "$PACKAGE_DIR"
print_success "Directory created"
echo ""

# ============================================
# INSTALL DEPENDENCIES
# ============================================

echo -e "${YELLOW}Step 3: Installing dependencies...${NC}"
echo "This may take a few minutes..."

# Create a temporary requirements file excluding dev dependencies
TEMP_REQ=$(mktemp)
grep -v "^#" "${BACKEND_DIR}/requirements.txt" | grep -v "pytest\|black\|flake8\|mypy" > "$TEMP_REQ" || true

# Install with better error handling
if pip3 install -r "$TEMP_REQ" -t "$PACKAGE_DIR" --quiet --no-cache-dir 2>&1 | tee /tmp/pip_install.log; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    cat /tmp/pip_install.log
    rm -f "$TEMP_REQ"
    exit 1
fi

rm -f "$TEMP_REQ"

# Clean up unnecessary files to reduce package size
echo "Cleaning up unnecessary files..."
find "$PACKAGE_DIR" -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PACKAGE_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$PACKAGE_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
print_success "Unnecessary files cleaned"
echo ""

# ============================================
# COPY APPLICATION CODE
# ============================================

echo -e "${YELLOW}Step 4: Copying application code...${NC}"

# Copy directories if they exist
if [ -d "${BACKEND_DIR}/agents" ]; then
    cp -r "${BACKEND_DIR}/agents" "$PACKAGE_DIR/"
    print_success "Copied agents/"
fi

if [ -d "${BACKEND_DIR}/config" ]; then
    cp -r "${BACKEND_DIR}/config" "$PACKAGE_DIR/"
    print_success "Copied config/"
fi

if [ -d "${BACKEND_DIR}/models" ]; then
    cp -r "${BACKEND_DIR}/models" "$PACKAGE_DIR/"
    print_success "Copied models/"
fi

# Copy main.py
cp "${BACKEND_DIR}/main.py" "$PACKAGE_DIR/"
print_success "Copied main.py"

# Copy any other Python files in backend root
for file in "${BACKEND_DIR}"/*.py; do
    if [ -f "$file" ] && [ "$(basename "$file")" != "main.py" ]; then
        cp "$file" "$PACKAGE_DIR/"
        print_success "Copied $(basename "$file")"
    fi
done

echo ""

# ============================================
# CREATE DEPLOYMENT ZIP
# ============================================

echo -e "${YELLOW}Step 5: Creating deployment ZIP...${NC}"
cd "$PACKAGE_DIR"

# Create ZIP with progress indicator
if zip -r "../lambda-deployment.zip" . -q; then
    print_success "ZIP file created"
else
    print_error "Failed to create ZIP file"
    cd ../..
    exit 1
fi

cd ../..
echo ""

# ============================================
# PACKAGE VALIDATION (with better error handling)
# ============================================

echo -e "${YELLOW}Step 6: Validating package...${NC}"

# Get file size (cross-platform)
FILESIZE_BYTES=$(get_file_size "$ZIP_FILE")
if [ -z "$FILESIZE_BYTES" ]; then
    print_warning "Could not determine file size, skipping size validation"
    FILESIZE="Unknown"
else
    FILESIZE=$(bytes_to_human "$FILESIZE_BYTES")
    echo "Package size: $FILESIZE ($FILESIZE_BYTES bytes)"
fi

# Try to get unzipped size (with error handling)
UNZIPPED_SIZE=0
UNZIPPED_SIZE_MB=0
if UNZIP_OUTPUT=$(unzip -l "$ZIP_FILE" 2>/dev/null); then
    UNZIPPED_SIZE=$(echo "$UNZIP_OUTPUT" | tail -1 | awk '{print $1}' 2>/dev/null || echo "0")
    if [ "$UNZIPPED_SIZE" -gt 0 ]; then
        UNZIPPED_SIZE_MB=$((UNZIPPED_SIZE / 1024 / 1024))
        echo "Estimated unzipped size: ${UNZIPPED_SIZE_MB} MB"
        
        # Validate size limits
        if [ "$UNZIPPED_SIZE" -gt "$MAX_LAMBDA_SIZE" ]; then
            print_error "Package too large! Unzipped size exceeds Lambda limit of 250 MB"
            print_warning "Consider using Lambda Layers for large dependencies"
            exit 1
        fi
        print_success "Package size within Lambda limits"
    fi
else
    print_warning "Could not determine unzipped size, skipping validation"
fi

# Determine upload method
UPLOAD_METHOD="UNKNOWN"
if [ -n "$FILESIZE_BYTES" ] && [ "$FILESIZE_BYTES" -gt 0 ]; then
    if [ "$FILESIZE_BYTES" -gt "$MAX_ZIP_SIZE" ]; then
        print_warning "ZIP file exceeds 50 MB - you'll need to upload via S3"
        UPLOAD_METHOD="S3"
    else
        print_success "ZIP file can be uploaded directly via console"
        UPLOAD_METHOD="DIRECT"
    fi
fi

# Count files (with error handling)
FILE_COUNT=0
if UNZIP_LIST=$(unzip -l "$ZIP_FILE" 2>/dev/null | tail -1); then
    FILE_COUNT=$(echo "$UNZIP_LIST" | awk '{print $2}' 2>/dev/null || echo "0")
    if [ "$FILE_COUNT" -gt 0 ]; then
        echo "Total files in package: $FILE_COUNT"
    fi
fi

echo ""

# ============================================
# DEPLOYMENT OPTIONS
# ============================================

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment package created successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "📦 Package location: $ZIP_FILE"
echo "📊 Package size: $FILESIZE"
if [ "$UNZIPPED_SIZE_MB" -gt 0 ]; then
    echo "📁 Unzipped size: ~${UNZIPPED_SIZE_MB} MB"
fi
if [ "$FILE_COUNT" -gt 0 ]; then
    echo "📄 Total files: $FILE_COUNT"
fi
echo ""

# Show deployment instructions based on package size
if [ "$UPLOAD_METHOD" = "S3" ]; then
    echo -e "${YELLOW}⚠️  Large Package Detected - S3 Upload Required${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Upload to S3:"
    echo "   aws s3 cp $ZIP_FILE s3://YOUR_BUCKET/lambda-deployment.zip"
    echo ""
    echo "2. Update Lambda function from S3:"
    echo "   aws lambda update-function-code \\"
    echo "     --function-name YOUR_FUNCTION_NAME \\"
    echo "     --s3-bucket YOUR_BUCKET \\"
    echo "     --s3-key lambda-deployment.zip"
elif [ "$UPLOAD_METHOD" = "DIRECT" ]; then
    echo "Next steps:"
    echo ""
    echo "Option 1: Manual Upload via Console"
    echo "  1. Go to AWS Lambda Console"
    echo "  2. Select your function (or create new)"
    echo "  3. Click 'Upload from' → '.zip file'"
    echo "  4. Upload: $ZIP_FILE"
    echo "  5. Set handler to: main.handler"
    echo "  6. Configure environment variables"
    echo ""
    
    if [ "$AWS_CLI_AVAILABLE" = true ]; then
        echo "Option 2: Deploy via AWS CLI"
        echo "  Run the following command:"
        echo ""
        echo "  aws lambda update-function-code \\"
        echo "    --function-name YOUR_FUNCTION_NAME \\"
        echo "    --zip-file fileb://$ZIP_FILE"
        echo ""
        
        # Offer automatic deployment
        read -p "Would you like to deploy now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter Lambda function name: " FUNCTION_NAME
            if [ -n "$FUNCTION_NAME" ]; then
                echo ""
                echo -e "${YELLOW}Deploying to Lambda function: $FUNCTION_NAME${NC}"
                if aws lambda update-function-code \
                    --function-name "$FUNCTION_NAME" \
                    --zip-file "fileb://$ZIP_FILE" \
                    --no-cli-pager; then
                    print_success "Deployment successful!"
                else
                    print_error "Deployment failed!"
                fi
            fi
        fi
    fi
else
    echo "Next steps:"
    echo "  1. Go to AWS Lambda Console"
    echo "  2. Upload: $ZIP_FILE"
    echo "  3. Set handler to: main.handler"
fi

echo ""
echo "📝 Configuration:"
echo "  Handler: main.handler"
echo "  Runtime: python3.10 (or later)"
echo "  Recommended memory: 512 MB - 1024 MB"
echo "  Recommended timeout: 60 - 300 seconds"
echo ""

# Check if env variables file exists
if [ -f "${BACKEND_DIR}/lambda-env-variables.txt" ]; then
    print_info "Environment variables template: ${BACKEND_DIR}/lambda-env-variables.txt"
fi

echo ""
echo -e "${YELLOW}Cleaning up temporary files...${NC}"
rm -rf "$PACKAGE_DIR"
print_success "Cleanup complete"
echo ""
echo -e "${GREEN}Done! 🚀${NC}"