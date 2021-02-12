import * as React from 'react'
import {Subtract} from "utility-types";
import {AuthHandling} from "./index";
import config from './Config'
import {UserResponse} from "./user/model";

export interface SignInResult {
    success: boolean;
    reason?: string;
}

class UserInformation {
    token: string
    email_address: string
    display_name: string | null
    is_approved: boolean
    avatar_image: string | null

    constructor(token: string, email_address: string, display_name: string | null, is_approved: boolean, avatar_image: string | null) {
        this.token = token
        this.email_address = email_address
        this.display_name = display_name
        this.is_approved = is_approved
        this.avatar_image = avatar_image
    }

    static delete(): void {
        localStorage.removeItem('user-profile');
    }

    static save(user_information: UserInformation): UserInformation {
        localStorage.setItem('user-profile', JSON.stringify(user_information));
        return user_information
    }

    static load(): UserInformation | null {
        const local_storage = localStorage.getItem('user-profile')
        if (local_storage) {
            return JSON.parse(local_storage) as UserInformation
        }
        return null
    }
}

export interface User {
    display_name: string | null;
}

export interface SignInResponse {
    token: string;
    is_approved: boolean;
    email_address: string;
    user: User;
}

interface ErrorMessage {
    detail: string;
}

export class TokenBasedAuthenticator {

    isSignedIn = false
    user_information: UserInformation | null = null

    static unsecure_headers(): Headers {
        const headers: HeadersInit = new Headers()
        headers.set('Content-Type', 'application/json')
        return headers
    }

    constructor() {
        this.user_information = UserInformation.load()
        if (this.user_information) {
            this.isSignedIn = true
        }
    }

    bearer_token(): string | null {
        if (!this.user_information) {
            return null
        }
        return `Bearer ${this.user_information?.token}`
    }

    async sign_in(email_address: string, password: string): Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/signin`, {
            headers:  TokenBasedAuthenticator.unsecure_headers(),
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                password: password,
            }),
        })

        return this._parseRequestForToken(response)
    }

    async sign_out(): Promise<void> {
        this.isSignedIn = false
        this.user_information = null
        UserInformation.delete()
        return Promise.resolve()
    }

    update_avatar_image(avatar_image: string | null): void {
        if (this.user_information) {
            this.user_information.avatar_image = avatar_image
            UserInformation.save(this.user_information)
        }
    }

    async change_password(email_address: string, current_password: string, new_password: string, new_password_repeated: string): Promise<SignInResult> {
        const response = await fetch(`${config.apihost}/user/change_password`, {
            headers:  TokenBasedAuthenticator.unsecure_headers(),
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                current_password: current_password,
                new_password: new_password,
                new_password_repeated: new_password_repeated,
            }),
        })

        return this._parseRequestForToken(response)
    }

    async sign_up(email_address: string, password: string, password_repeated: string): Promise<SignInResult> {
        const headers: HeadersInit = new Headers()
        headers.set('Content-Type', 'application/json')
        const response = await fetch(`${config.apihost}/user/signup`, {
            headers:  headers,
            method: "POST",
            body: JSON.stringify({
                email_address: email_address,
                password: password,
                password_repeated: password_repeated,
            }),
        })

        return this._parseRequestForToken(response)
    }

    update_user_information(userResponse: UserResponse): void {
        if (this.user_information) {
            this.user_information.display_name = userResponse.display_name
            this.user_information.is_approved = userResponse.is_approved
            UserInformation.save(this.user_information)
        }
    }

    async _parseRequestForToken(response: Response): Promise<SignInResult> {
        if (response.status === 200) {
            const json_response = await response.json() as SignInResponse
            this.user_information = {
                token: json_response.token,
                email_address: json_response.email_address,
                display_name: json_response.user.display_name || '',
                is_approved: json_response.is_approved,
                avatar_image: null,
            }
            UserInformation.save(this.user_information)
            this.isSignedIn = true
            return Promise.resolve({
                success: true
            })
        }
        else if (response.status === 401) {
            const json_response = await response.json() as ErrorMessage
            return Promise.resolve({
                success: false,
                reason: json_response.detail
            })
        }
        return Promise.resolve({
            success: false,
            reason: "Unknown error"
        })

    }
}

export interface WithAuthHandling {
    authHandling: TokenBasedAuthenticator;
}


// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export const withAuthHandling = <P extends WithAuthHandling>(Component: React.ComponentType<P>) =>
    class WithGoogleAuthHandler extends React.Component<Subtract<P, WithAuthHandling>> {

        render(): JSX.Element {
            return <AuthHandling.Consumer>
                {(value): JSX.Element =>
                    <Component
                        {...this.props as P}
                        authHandling={value}
                    />
                }
            </AuthHandling.Consumer>

        }
    }
