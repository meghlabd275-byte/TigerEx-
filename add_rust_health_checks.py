#!/usr/bin/env python3
"""
Script to add health check endpoints to Rust services
"""

import os

def add_health_check_to_rust_service(service_path):
    """Add health check endpoint to a Rust service"""
    main_rs_path = os.path.join(service_path, "src", "main.rs")
    
    if not os.path.exists(main_rs_path):
        return False
    
    with open(main_rs_path, "r") as f:
        content = f.read()
    
    # Check if health endpoint already exists
    if "/health" in content:
        return False
    
    # Add health check function
    health_check_fn = '''
// Health check endpoint
async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(json!({
        "status": "healthy",
        "service": "''' + os.path.basename(service_path) + '''"
    }))
}
'''
    
    # Add the health check function before the main function
    content = content.replace(
        "use actix_web::{web, App, HttpServer, HttpResponse, Responder};",
        "use actix_web::{web, App, HttpServer, HttpResponse, Responder};\nuse serde_json::json;"
    )
    
    # Add the health check route
    if ".route(" in content:
        # Find the first route and add health check before it
        content = content.replace(
            ".route(",
            ".route(&quot;/health&quot;, web::get().to(health_check))\n            .route("
        )
        
        # Add the health check function
        content = health_check_fn + "\n" + content
    else:
        # Add at the beginning of the file
        content = health_check_fn + "\n" + content
    
    with open(main_rs_path, "w") as f:
        f.write(content)
    
    return True

def main():
    """Main function"""
    services_dir = "backend"
    
    # Rust services that need health checks
    rust_services = [
        "derivatives-engine",
        "trading-engine",
        "transaction-engine"
    ]
    
    updated_services = []
    
    for service_name in rust_services:
        service_path = os.path.join(services_dir, service_name)
        if os.path.exists(service_path):
            if add_health_check_to_rust_service(service_path):
                updated_services.append(service_name)
    
    print(f"Added health checks to {len(updated_services)} Rust services:")
    for service in updated_services:
        print(f"  - {service}")

if __name__ == "__main__":
    main()