class UserProfile {
    givenName;
    familyName;
    email;
    avatarUrl;
    access_token;
    id_token;

    constructor(givenName, familiyName, email, avatarUrl, access_token, id_token) {
        this.givenName  = givenName;
        this.familyName = familiyName;
        this.email = email;
        this.avatarUrl = avatarUrl;
        this.access_token = access_token;
        this.id_token  = id_token;
    }

    get bearerToken() {
        return 'Bearer ' + this.id_token;
    }

    static delete() {
        localStorage.removeItem('user-profile');
    }
    
    static save(userProfile) {
        localStorage.setItem('user-profile', JSON.stringify(userProfile));
        return userProfile;
    }

    merge(fields) {
        this.familyName = fields.familyName;
        this.givenName = fields.givenName;

        UserProfile.save(this);
    }

    static load() {
        const data = localStorage.getItem('user-profile');
        if (data === undefined) {
            return null;
        }
        const jsonData = JSON.parse(data);
        if (jsonData === null) {
            return null;
        }
        return new UserProfile(
            jsonData.givenName,
            jsonData.familyName,
            jsonData.email,
            jsonData.avatarUrl,
            jsonData.access_token,
            jsonData.id_token,
        );
    }
}

export default UserProfile;