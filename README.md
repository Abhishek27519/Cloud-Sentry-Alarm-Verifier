# 🛡️ CloudSentry: Serverless ML Alarm Verification Microservice

An enterprise-grade, event-driven serverless microservice engineered to intercept real-time telemetry alerts, analyze operational metrics, and classify system anomalies to filter out false alarms.

This repository showcases an advanced cloud architecture designed to bypass strict serverless environment constraints using dynamic object-storage side-loading patterns.

---

## 🏗️ System Architecture & Workflow

The entire infrastructure runs completely stateless and serverless, utilizing a high-throughput, decoupled pipeline:

```text
[ Client / Postman ]
│
▼ (Secure HTTPS POST)
[ Amazon API Gateway ]
│
▼ (Proxy Request Payload)
[ AWS Lambda Function ] ◄─── (Init Execution: Streams heavy ML binaries) ─── [ Amazon S3 Bucket ]
│
├─► Local Ephemeral Storage (/tmp) ──► Dynamic sys.path Injection
│
▼ (Inference Processing via ExtraTreeRegressor Engine)
[ Formatted JSON Response ] ──► (HTTP 200 OK back to Client)

* **Ingress:** The client triggers an alert verification by issuing a secure HTTPS POST request.

* **Decoupling Layer:** Amazon API Gateway catches the traffic, authorizes the payload structure, and maps it directly to an execution event thread.

* **Compute Core:** AWS Lambda initializes a micro-container. If it is a Cold Start, it programmatically intercepts the dependency bundle from Amazon S3, unzips it into local memory, dynamically maps the execution path, runs the local machine learning pipeline, and evaluates the incoming data.

* **Egress:** The client receives a clean, actionable json response mapping the machine learning prediction model.

---

## 🛠️ AWS Services & Core Technical Tools Defined

### 1. Amazon API Gateway
Acts as the "Front Door" for the microservice. Instead of exposing our compute core directly to the public internet, API Gateway acts as a reverse proxy handler.

* **Why it's used:** It handles cross-cutting concerns like SSL/TLS termination, automated cross-origin resource sharing (CORS) pre-flight checks, and robust request filtering before passing data to our functional business tier.

### 2. AWS Lambda
A serverless, event-driven compute execution layer that runs the backend inference script without requiring provisioning, patching, or maintaining 24/7 server infrastructure.

* **Why it's used:** It scales execution instances automatically to match traffic spikes and operates under a billing profile measured down to the millisecond—meaning zero operational costs when the application is sitting idle.

### 3. Amazon S3 (Simple Storage Service)
An ultra-durable, highly available object storage service used to hold application artifacts completely separate from the execution compute layer.

* **Why it's used:** Because AWS Lambda enforces a strict 250 MB unzipped deployment package limit, heavy ML modules like scikit-learn and pandas cannot be bundled traditionally. S3 acts as an external decoupled staging environment to bypass this hardware restriction.

### 4. Scikit-Learn (ExtraTreeRegressor)
An advanced ensemble machine learning model framework used to evaluate incoming data vectors (duration, severity, frequency) and return highly accurate, deterministic classification predictions.

---

## 💡 The Core Engineering Innovation: Runtime Side-Loading

To run heavy data science architectures on an ephemeral Lambda function, this project implements a custom Runtime Side-Loading Architecture:

* **Step 1 (AWS CloudShell):** Cross-compiled heavy library binaries natively using target architecture compilation flags (`--platform manylinux2014_x86_64 --python-version 3.12 --only-binary=:all:`).

* **Step 2 (Amazon S3):** Packaged the cross-compiled environment into `ml_libs.zip` and staged it alongside `alarm_model.joblib` inside a secure object storage bucket.

* **Step 3 (Lambda Init Phase):** At execution initialization (Cold Start), the handler utilizes `boto3` to stream the ZIP archive straight into the ephemeral `/tmp` filesystem scratchpad (which supports up to 10 GB of space).

* **Step 4 (Runtime Injection):** Programmatically extracted the ZIP and altered Python's global runtime lookup parameters using `sys.path.insert(0, "/tmp/python")` before triggering core library imports.

---

## 📂 Repository Layout

```text
CloudSentryML/
├── src/
│   └── lambda_function.py      # Serverless engine handler managing S3 side-loading and inference logic
├── training/
│   ├── alarm_data.csv          # Telemetry database containing historical alert training metrics
│   └── generate_and_train.py   # Offline ML training pipeline script used to train and serialize the model
├── .gitignore                  # Active tracking exclusions protecting GitHub from heavy files (.joblib, .zip, venv/)
└── README.md                   # Comprehensive system architectural design document

---

## 🧪 Comprehensive Testing Process

The application was validated end-to-end to ensure structural integrity across network layers, correct payload transformations, and deterministic model behavior.

### 1. Offline Verification (Local Pipeline Validation)
Before pushing changes to the cloud, the machine learning compilation phase was tested locally using `generate_and_train.py`.

* **Action:** Running the training asset reads telemetry data out of `alarm_data.csv`, evaluates model score accuracy metrics, and exports a serialized `alarm_model.joblib` binary payload file verifying script logic.

### 2. Live REST API Contract Integration Testing
Once deployed on AWS, integration verification was handled via programmatic HTTP clients (such as Postman) hitting the live Gateway proxy endpoint.

* **API Endpoint Ingress:** `POST https://<api-gateway-id>.execute-api.us-east-2.amazonaws.com/verify`
* **Content-Type Header:** `application/json`

#### Test Case A: Anomaly Alert Payload Evaluation

```json
{
  "duration": 450,
  "severity": 9,
  "frequency": 12
}

* **Expected Response Status: HTTP 200 OK

* **Expected Payload Output:

```json
{
  "prediction": "True Anomaly",
  "input_received": { "duration": 450, "severity": 9, "frequency": 12 }
}

#### Test Case B: False Alarm Metric Validation

```json
{
  "duration": 25,
  "severity": 1,
  "frequency": 2
}

* **Expected Response Status: HTTP 200 OK

* **Expected Payload Output:

```json
{
  "prediction": "False Alarm",
  "input_received": { "duration": 25, "severity": 1, "frequency": 2 }
}

---

## 📈 Performance & Execution Benchmarks

* **Cold Start Latency:** ~8.5 seconds during initial hardware allocation, network streaming of assets from Amazon S3, and dependency decompression on the `/tmp` local storage path.

* **Warm Start Latency:** ~329 ms on subsequent API executions, running instantly out of container cache and providing high-speed REST operations.

---