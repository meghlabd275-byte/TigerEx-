/**
 * TigerEx Flutter Social Login
 * iOS & Android
 */
import 'package:flutter/material.dart';
import 'package:flutter_auth_buttons/flutter_auth_buttons.dart';

void main() => runApp(TigerExSocialApp());

class TigerExSocialApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TigerEx Social Login',
      home: SocialLoginPage(),
    );
  }
}

class SocialLoginPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFF0B0E11),
      body: Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('🐯 TigerEx', style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Color(0xFFF0B90B))),
              SizedBox(height: 8),
              Text('Continue with your social account', style: TextStyle(color: Colors.grey)),
              SizedBox(height: 40),
              
              // Social Buttons Grid
              Wrap(
                spacing: 12, runSpacing: 12,
                alignment: WrapAlignment.center,
                children: [
                  _SocialButton(icon: '🔴', label: 'Google', color: Color(0xFF4285F4), onTap: () => _login('google')),
                  _SocialButton(icon: '🍎', label: 'Apple', color: Colors.black, onTap: () => _login('apple')),
                  _SocialButton(icon: '📘', label: 'Facebook', color: Color(0xFF1877F2), onTap: () => _login('facebook')),
                  _SocialButton(icon: '🐙', label: 'GitHub', color: Color(0xFF333333), onTap: () => _login('github')),
                  _SocialButton(icon: '🐦', label: 'Twitter', color: Color(0xFF1DA1F2), onTap: () => _login('twitter')),
                  _SocialButton(icon: '💬', label: 'Discord', color: Color(0xFF5865F2), onTap: () => _login('discord')),
                  _SocialButton(icon: '✈️', label: 'Telegram', color: Color(0xFF0088CC), onTap: () => _login('telegram')),
                  _SocialButton(icon: '💚', label: 'LINE', color: Color(0xFF00B900), onTap: () => _login('line')),
                  _SocialButton(icon: '💚', label: 'WeChat', color: Color(0xFF07C160), onTap: () => _login('wechat')),
                  _SocialButton(icon: '💛', label: 'Kakao', color: Color(0xFFFEE500), textColor: Color(0xFF3C1E1E), onTap: () => _login('kakao')),
                  _SocialButton(icon: '🪟', label: 'Microsoft', color: Color(0xFF00A4EF), onTap: () => _login('microsoft')),
                  _SocialButton(icon: '💼', label: 'LinkedIn', color: Color(0xFF0A66C2), onTap: () => _login('linkedin')),
                ],
              ),
              
              SizedBox(height: 30),
              Text('By continuing, you agree to TigerEx\nTerms of Service', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey, fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }
  
  void _login(String provider) {
    print('Social login with: $provider');
    // Implement OAuth flow here
  }
}

class _SocialButton extends StatelessWidget {
  final String icon, label;
  final Color color, textColor;
  final VoidCallback onTap;
  
  const _SocialButton({required this.icon, required this.label, required this.color, this.textColor = Colors.white, required this.onTap});
  
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(10)),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(icon, style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Text(label, style: TextStyle(color: textColor, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}
