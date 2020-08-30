interface UserProfileInterface {
    givenName: string;
    familyName: string;
    email: string;
    avatarUrl: string;
    access_token: string;
    id_token: string;
}

export default class UserProfile {
    readonly givenName: string;
    readonly familyName: string;
    readonly email: string;
    readonly avatarUrl: string;
    readonly access_token: string;
    readonly id_token: string;

    constructor(givenName: string, familiyName: string, email: string, avatarUrl: string, access_token: string, id_token: string) {
        this.givenName = givenName;
        this.familyName = familiyName;
        this.email = email;
        this.avatarUrl = avatarUrl;
        this.access_token = access_token;
        this.id_token = id_token;
    }

    get bearerToken(): string {
        return 'Bearer ' + this.id_token
    }

    static delete(): void {
        localStorage.removeItem('user-profile');
    }

    static save(userProfile: UserProfile): UserProfile {
        localStorage.setItem('user-profile', JSON.stringify(userProfile));
        return userProfile;
    }

    static get(): UserProfile {
        const userProfile = UserProfile.load()
        if (userProfile == null) {
            throw new Error("UserProfile may not be null.")
        }
        return userProfile
    }

    static load(): UserProfile | null {
        const data = localStorage.getItem('user-profile');
        if (data == null) {
            return null;
        }
        const upi = JSON.parse(data) as UserProfileInterface;
        return new UserProfile(
            upi.givenName, upi.familyName, upi.email, upi.avatarUrl, upi.access_token, upi.id_token
        )
    }
}
