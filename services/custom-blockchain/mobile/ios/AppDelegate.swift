import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        window = UIWindow(frame: UIScreen.main.bounds)
        window?.rootViewController = LoginViewController()
        window?.makeKeyAndVisible()
        return true
    }
}

class LoginViewController: UIViewController {
    // Social login buttons
    let googleBtn = UIButton(type: .system)
    let facebookBtn = UIButton(type: .system)
    let appleBtn = UIButton(type: .system)
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 0.1, green: 0.1, blue: 0.15, alpha: 1)
        setupUI()
    }
    
    func setupUI() {
        // Configure buttons for social login
    }
    
    @objc func socialLogin(_ provider: String) {
        // Show bind dialog
        showBindDialog()
    }
    
    func showBindDialog() {
        let alert = UIAlertController(title: "Bind Email & Phone", message: "Please bind your email and phone", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}
