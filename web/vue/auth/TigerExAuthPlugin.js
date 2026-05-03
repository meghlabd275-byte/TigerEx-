/**
 * TigerEx Vue Authentication Plugin
 * 
 * @version 1.0.0
 */

export default {
    
    install(Vue, options) {
        
        const TOKEN_KEY = 'tigerex_token';
        const USER_KEY = 'tigerex_user';
        const EXPIRY_KEY = 'tigerex_token_expiry';
        
        // Computed properties
        const isLoggedIn = () => {
            const token = localStorage.getItem(TOKEN_KEY);
            if (!token) return false;
            
            const expiry = localStorage.getItem(EXPIRY_KEY);
            if (expiry && new Date(expiry) < new Date()) {
                return false;
            }
            return true;
        };
        
        const getUser = () => {
            const data = localStorage.getItem(USER_KEY);
            return data ? JSON.parse(data) : null;
        };
        
        const getEmail = () => {
            const user = getUser();
            return user?.email || '';
        };
        
        const getDisplayName = () => {
            const user = getUser();
            if (user?.name) return user.name;
            const email = getEmail();
            return email ? email.split('@')[0] : 'User';
        };
        
        const getAvatar = () => {
            return getDisplayName()[0].toUpperCase();
        };
        
        // Methods
        const login = (user) => {
            if (!user?.email) return false;
            
            const token = 'tigerex_token_' + Date.now();
            const expiry = new Date();
            expiry.setHours(expiry.getHours() + 24);
            
            localStorage.setItem(TOKEN_KEY, token);
            localStorage.setItem(USER_KEY, JSON.stringify(user));
            localStorage.setItem(EXPIRY_KEY, expiry.toISOString());
            
            return true;
        };
        
        const logout = () => {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
            localStorage.removeItem(EXPIRY_KEY);
        };
        
        // Add to prototype
        Vue.prototype.$auth = {
            isLoggedIn,
            getUser,
            getEmail,
            getDisplayName,
            getAvatar,
            login,
            logout
        };
        
        // Reactive state
        const authState = Vue.observable({
            isLoggedIn: isLoggedIn(),
            user: getUser(),
            email: getEmail(),
            name: getDisplayName(),
            avatar: getAvatar()
        });
        
        Vue.prototype.$authstate = authState;
        
        // Mixin for route guards
        Vue.mixin({
            beforeRouteEnter(to, from, next) {
                if (to.meta?.requiresAuth && !isLoggedIn()) {
                    next({ path: '/login', query: { redirect: to.fullPath } });
                } else if (to.meta?.requiresGuest && isLoggedIn()) {
                    next({ path: '/dashboard' });
                } else {
                    next();
                }
            }
        });
    }
};<script>
export const useWallet = () => ({ createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }) })
</script>

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
