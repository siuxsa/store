def register_all_routes(app):
    from routes.auth import register_auth_routes
    from routes.frontend import register_frontend_routes
    from routes.orders import register_orders_routes
    from routes.telemetry import register_telemetry_routes
    from routes.admin.panel import register_admin_panel_routes
    from routes.admin.theme import register_admin_theme_routes
    from routes.admin.products import register_admin_products_routes
    from routes.admin.posts import register_admin_posts_routes
    from routes.admin.orders import register_admin_orders_routes
    from routes.admin.users import register_admin_users_routes
    from routes.admin.reviews import register_admin_reviews_routes
    from routes.admin.comments import register_admin_comments_routes
    from routes.admin.settings import register_admin_settings_routes
    from routes.admin.tool_requests import register_admin_tool_request_routes

    register_auth_routes(app)
    register_frontend_routes(app)
    register_orders_routes(app)
    register_telemetry_routes(app)
    register_admin_panel_routes(app)
    register_admin_theme_routes(app)
    register_admin_products_routes(app)
    register_admin_posts_routes(app)
    register_admin_orders_routes(app)
    register_admin_users_routes(app)
    register_admin_reviews_routes(app)
    register_admin_comments_routes(app)
    register_admin_settings_routes(app)
    register_admin_tool_request_routes(app)
