env

mongo -- "$MONGO_INITDB_DATABASE" <<EOF
    use admin
    var rootUser = '$MONGO_INITDB_ROOT_USERNAME';
    var rootPassword = '$MONGO_INITDB_ROOT_PASSWORD';
    var admin = db.getSiblingDB('admin');
    admin.auth(rootUser, rootPassword);

    use newsroom

    var user = '$MONGO_USER';
    var password = '$MONGO_PASS';
    var database = '$MONGO_DB';
    db.createUser({user: user, pwd: password, roles: ["readWrite"]});

    db.grantRolesToUser(
      user,
      [
        { role: "readWrite", db: database }
      ]
    )

EOF