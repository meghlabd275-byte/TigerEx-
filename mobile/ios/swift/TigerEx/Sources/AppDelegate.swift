import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = UINavigationController(rootViewController: LoginViewController())
        window?.makeKeyAndVisible()
        
        return true
    }
}

// MARK: - Login View Controller
class LoginViewController: UIViewController {
    
    // Test code for all verifications
    let TEST_CODE = "727752"
    
    // UI Elements
    private let scrollView = UIScrollView()
    private let contentView = UIView()
    
    private let logoLabel: UILabel = {
        let label = UILabel()
        label.text = "🐯 TigerEx"
        label.font = UIFont.systemFont(ofSize: 36, weight: .bold)
        label.textColor = UIColor(red: 240/255, green: 185/255, blue: 11/255, alpha: 1)
        label.textAlignment = .center
        return label
    }()
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "Login to your account"
        label.font = UIFont.systemFont(ofSize: 16)
        label.textColor = .gray
        label.textAlignment = .center
        return label
    }()
    
    private lazy var tabSegment: UISegmentedControl = {
        let segment = UISegmentedControl(items: ["Email", "Phone"])
        segment.selectedSegmentIndex = 0
        segment.backgroundColor = UIColor(red: 43/255, green: 49/255, blue: 57/255, alpha: 1)
        segment.selectedSegmentTintColor = UIColor(red: 240/255, green: 185/255, blue: 11/255, alpha: 1)
        segment.setTitleTextAttributes([.foregroundColor: UIColor.white], for: .normal)
        segment.setTitleTextAttributes([.foregroundColor: UIColor.black], for: .selected)
        segment.addTarget(self, action: #selector(tabChanged), for: .valueChanged)
        return segment
    }()
    
    private let emailTextField: UITextField = {
        let tf = UITextField()
        tf.placeholder = "Enter your email"
        tf.backgroundColor = UIColor(red: 43/255, green: 49/255, blue: 57/255, alpha: 1)
        tf.textColor = .white
        tf.layer.cornerRadius = 8
        tf.leftView = UIView(frame: CGRect(x: 0, y: 0, width: 16, height: 0))
        tf.leftViewMode = .always
        tf.keyboardType = .emailAddress
        tf.autocapitalizationType = .none
        return tf
    }()
    
    private let passwordTextField: UITextField = {
        let tf = UITextField()
        tf.placeholder = "Password"
        tf.backgroundColor = UIColor(red: 43/255, green: 49/255, blue: 57/255, alpha: 1)
        tf.textColor = .white
        tf.layer.cornerRadius = 8
        tf.leftView = UIView(frame: CGRect(x: 0, y: 0, width: 16, height: 0))
        tf.leftViewMode = .always
        tf.isSecureTextEntry = true
        return tf
    }()
    
    private let loginButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Sign In", for: .normal)
        button.setTitleColor(.black, for: .normal)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .bold)
        button.backgroundColor = UIColor(red: 240/255, green: 185/255, blue: 11/255, alpha: 1)
        button.layer.cornerRadius = 8
        return button
    }()
    
    private let otpView: UIView = {
        let view = UIView()
        view.isHidden = true
        return view
    }()
    
    private let otpTextField: UITextField = {
        let tf = UITextField()
        tf.placeholder = "000000"
        tf.textAlignment = .center
        tf.font = UIFont.systemFont(ofSize: 24)
        tf.backgroundColor = UIColor(red: 43/255, green: 49/255, blue: 57/255, alpha: 1)
        tf.textColor = .white
        tf.layer.cornerRadius = 8
        tf.keyboardType = .numberPad
        return tf
    }()
    
    private let verifyButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Verify", for: .normal)
        button.setTitleColor(.black, for: .normal)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .bold)
        button.backgroundColor = UIColor(red: 240/255, green: 185/255, blue: 11/255, alpha: 1)
        button.layer.cornerRadius = 8
        button.isHidden = true
        return button
    }()
    
    private let activityIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.color = .white
        indicator.hidesWhenStopped = true
        return indicator
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
        setupActions()
    }
    
    private func setupUI() {
        view.backgroundColor = UIColor(red: 11/255, green: 14/255, blue: 17/255, alpha: 1)
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        [logoLabel, titleLabel, tabSegment, emailTextField, passwordTextField, 
         loginButton, otpView, otpTextField, verifyButton, activityIndicator].forEach {
            contentView.addSubview($0)
        }
        
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
    }
    
    private func setupConstraints() {
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        contentView.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            logoLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 60),
            logoLabel.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            
            titleLabel.topAnchor.constraint(equalTo: logoLabel.bottomAnchor, constant: 8),
            titleLabel.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            
            tabSegment.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 40),
            tabSegment.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            tabSegment.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            tabSegment.heightAnchor.constraint(equalToConstant: 48),
            
            emailTextField.topAnchor.constraint(equalTo: tabSegment.bottomAnchor, constant: 24),
            emailTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            emailTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            emailTextField.heightAnchor.constraint(equalToConstant: 56),
            
            passwordTextField.topAnchor.constraint(equalTo: emailTextField.bottomAnchor, constant: 16),
            passwordTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            passwordTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            passwordTextField.heightAnchor.constraint(equalToConstant: 56),
            
            loginButton.topAnchor.constraint(equalTo: passwordTextField.bottomAnchor, constant: 32),
            loginButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            loginButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            loginButton.heightAnchor.constraint(equalToConstant: 56),
            
            otpTextField.topAnchor.constraint(equalTo: loginButton.bottomAnchor, constant: 32),
            otpTextField.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            otpTextField.widthAnchor.constraint(equalToConstant: 200),
            otpTextField.heightAnchor.constraint(equalToConstant: 56),
            
            verifyButton.topAnchor.constraint(equalTo: otpTextField.bottomAnchor, constant: 24),
            verifyButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            verifyButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            verifyButton.heightAnchor.constraint(equalToConstant: 56),
            verifyButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -40),
            
            activityIndicator.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: contentView.centerYAnchor)
        ])
    }
    
    private func setupActions() {
        loginButton.addTarget(self, action: #selector(loginTapped), for: .touchUpInside)
        verifyButton.addTarget(self, action: #selector(verifyTapped), for: .touchUpInside)
    }
    
    @objc private func tabChanged() {
        if tabSegment.selectedSegmentIndex == 0 {
            emailTextField.placeholder = "Enter your email"
            emailTextField.keyboardType = .emailAddress
        } else {
            emailTextField.placeholder = "Phone number"
            emailTextField.keyboardType = .phonePad
        }
    }
    
    @objc private func loginTapped() {
        guard let identifier = emailTextField.text, !identifier.isEmpty,
              let password = passwordTextField.text, !password.isEmpty else {
            showAlert(message: "Please enter email/phone and password")
            return
        }
        
        activityIndicator.startAnimating()
        loginButton.isEnabled = false
        
        // Simulate API call
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            self?.activityIndicator.stopAnimating()
            self?.showOTPView()
        }
    }
    
    private func showOTPView() {
        emailTextField.isHidden = true
        passwordTextField.isHidden = true
        loginButton.isHidden = true
        
        otpTextField.isHidden = false
        verifyButton.isHidden = false
    }
    
    @objc private func verifyTapped() {
        guard let code = otpTextField.text, !code.isEmpty else {
            showAlert(message: "Please enter verification code")
            return
        }
        
        if code == TEST_CODE {
            showAlert(message: "✓ Verification successful!")
            showMainScreen()
        } else {
            showAlert(message: "Invalid code. Use: \(TEST_CODE)")
        }
    }
    
    private func showMainScreen() {
        let mainVC = MainViewController()
        navigationController?.pushViewController(mainVC, animated: true)
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    private func showAlert(message: String) {
        let alert = UIAlertController(title: "TigerEx", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - Main View Controller
class MainViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        view.backgroundColor = UIColor(red: 11/255, green: 14/255, blue: 17/255, alpha: 1)
        
        let label = UILabel()
        label.text = "✓ Welcome to TigerEx!"
        label.textColor = UIColor(red: 0/255, green: 192/255, blue: 135/255, alpha: 1)
        label.font = UIFont.systemFont(ofSize: 24, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(label)
        
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            label.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
}
