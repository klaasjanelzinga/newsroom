import {UserProfileResponse} from "./model";


export class UserProfileNotFoundException extends Error {}


export default class UserProfile {
    readonly givenName: string;
    readonly familyName: string;
    readonly email: string;
    readonly avatarUrl: string;
    readonly id_token: string;

    constructor(givenName: string, familiyName: string, email: string, avatarUrl: string, id_token: string) {
        this.givenName = givenName;
        this.familyName = familiyName;
        this.email = email;
        this.avatarUrl = avatarUrl;
        this.id_token = id_token;
    }

    static delete(): void {
        localStorage.removeItem('user-profile');
    }

    static save(userProfile: UserProfileResponse): UserProfile {
        localStorage.setItem('user-profile', JSON.stringify(userProfile));
        return new UserProfile(userProfile.given_name, userProfile.family_name, userProfile.email, userProfile.avatar_url, userProfile.id_token);
    }

    static get(): UserProfile {
        const userProfile = UserProfile.load()
        if (userProfile == null) {
            throw new UserProfileNotFoundException("UserProfile may not be null.")
        }
        return userProfile
    }

    static load(): UserProfile | null {
        const data = localStorage.getItem('user-profile');
        if (data == null) {
            return null;
        }
        const upi = JSON.parse(data) as UserProfileResponse;
        return new UserProfile(upi.given_name, upi.family_name, upi.email, upi.avatar_url, upi.id_token)
    }
}
