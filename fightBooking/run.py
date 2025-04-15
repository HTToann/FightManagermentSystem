from configs import app
import apis  # import blueprint

# Đăng ký blueprint
app.register_blueprint(apis.search_bp)
app.register_blueprint(apis.payment_bp)
app.register_blueprint(apis.search_detail_bp)
if __name__ == "__main__":
    app.run(debug=True)
