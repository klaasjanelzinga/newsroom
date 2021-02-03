export class GoogleAuthHandling {

    googleAuth: gapi.auth2.GoogleAuth | null = null
    currentUser: gapi.auth2.GoogleUser | null = null
    is_ready = false
    isSignedIn = false
    some_special_token = "it's here"

    constructor() {
        const script = document.createElement("script");
        script.src = "https://apis.google.com/js/platform.js";
        script.async = true;
        script.onload = () => this.scriptLoaded();
        document.body.appendChild(script);
    }

    _sleep(ms: number) : Promise<void> {
        return new Promise(
            resolve => setTimeout(resolve, ms)
        )
    }

    async wait_for_ready() : Promise<void> {
        while (!this.is_ready) {
            await this._sleep(100)
        }
    }

    async sign_out() : Promise<void> {
        await this.wait_for_ready()
        this.googleAuth?.signOut()
    }

    async sign_in() : Promise<gapi.auth2.GoogleUser> {
        await this.wait_for_ready()
        if (!this.googleAuth) {
            throw new Error("Google authentication not found.")
        }
        const options = new gapi.auth2.SigninOptionsBuilder()
        options.setPrompt('consent')
        return this.googleAuth.signIn(options)
    }

    async authResponse() : Promise<gapi.auth2.AuthResponse> {
        await this.wait_for_ready()
        if (!this.currentUser) {
            throw new Error("Google user is not set.")
        }
        return this.currentUser?.getAuthResponse()
    }

    scriptLoaded() : void {
        gapi.load('auth2', this.gapi_loaded)
    }

    isSignedInListener = (isSignedIn: boolean) : void => {
        this.isSignedIn = isSignedIn
    }

    currentUserListener = (currentUser: gapi.auth2.GoogleUser) : void => {
        this.currentUser = currentUser
    }

    gapi_loaded = () : void => {
        gapi.auth2.init({
            client_id: '662875567592-9do93u1nppl2ks4geufjtm7n5hfo23m3.apps.googleusercontent.com',
            scope: 'openid profile email'
        }).then(() => {
            this.googleAuth = gapi.auth2.getAuthInstance()
            this.googleAuth.isSignedIn.listen(this.isSignedInListener)
            this.googleAuth.currentUser.listen(this.currentUserListener)
            this.isSignedInListener(this.googleAuth.isSignedIn.get())
            this.currentUserListener(this.googleAuth.currentUser.get())
            this.is_ready = true
        })
    }

}

