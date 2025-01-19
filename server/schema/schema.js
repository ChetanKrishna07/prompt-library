const Prompt = require("../models/Prompt")
const User = require("../models/User")

const {
    GraphQLObjectType,
    GraphQLID,
    GraphQLString,
    GraphQLList,
    GraphQLNonNull,
    GraphQLSchema
} = require('graphql')

const UserType = new GraphQLObjectType({
    name: 'User',
    fields: () => ({
        id: {type: GraphQLID},
        username: {type: GraphQLString},
        email: {type: GraphQLString},
        password: {type: GraphQLString},
    })
})

const PromptType = new GraphQLObjectType({
    name: 'Prompt',
    fields: () => ({
        id: {type: GraphQLID},
        template: {type: GraphQLString},
        variables: {type: GraphQLList(GraphQLString)},
        user: {
            type: UserType,
            resolve(parent, args) {
                return User.findOne({username: parent.username})
            }
        }
    })
})

const RootQuery = new GraphQLObjectType({
    name: 'RootQueryType',
    fields: {
        users: {
            type: GraphQLList(UserType),
            resolve(parent, args) {
                return User.find()
            }
        },
        user: {
            type: UserType,
            args: {username: {type: GraphQLString}},
            resolve(parent, args) {
                return User.findOne({username: args.username})
            }
        },
        prompts: {
            type: GraphQLList(PromptType),
            resolve(parent, args) {
                return Prompt.find()
            }
        },
        prompt: {
            type: PromptType,
            args: {id: {type: GraphQLID}},
            resolve(parent, args) {
                return User.findById(args.id)
            }
        }
    }
})

// Mutations
const mutation = new GraphQLObjectType({
    name: 'Mutation',
    fields: {
        addUser: {
            type: UserType,
            args: {
                username: {
                    type: GraphQLNonNull(GraphQLString)
                },
                email: {
                    type: GraphQLNonNull(GraphQLString)
                },
                password: {
                    type: GraphQLNonNull(GraphQLString)
                }
            },
            resolve(parent, args) {
                const user = new User({
                    username: args.username,
                    email: args.email,
                    password: args.password
                })
                return user.save()
            }
        },
        deleteUser: {
            type: UserType,
            args: {
                username: {
                    type: GraphQLNonNull(GraphQLString)
                }
            },
            resolve(parent, args) {
                return User.findOneAndDelete({username: args.username})
            }
        },
        updateUser: {
            type: UserType,
            args: {
                username: {
                    type: GraphQLNonNull(GraphQLString)
                },
                email: {
                    type: GraphQLString
                },
                password: {
                    type: GraphQLString
                }
            },
            resolve(parent, args) {
                return User.findOneAndUpdate(
                    {username: args.username},
                    {
                        $set: {
                            email: args.email,
                            password: args.password
                        }
                    },
                    {
                        new: true
                    }
                )
            }
        },
        addPrompt : {
            type: PromptType,
            args: {
                template: {
                    type: GraphQLNonNull(GraphQLString)
                },
                variables: {
                    type: GraphQLNonNull(GraphQLList(GraphQLString))
                },
                username: {
                    type: GraphQLString,
                    defaultValue: "root"
                }
            },
            resolve(parent, args) {
                const prompt = new Prompt({
                    template: args.template,
                    variables: args.variables,
                    username: args.username
                })

                return prompt.save()
            }
        },
        deletePrompt: {
            type: PromptType,
            args: {
                id: {
                    type: GraphQLNonNull(GraphQLID)
                }
            },
            resolve(parent, args) {
                return Prompt.findByIdAndDelete(args.id)
            }
        },
        updatePrompt: {
            type: PromptType,
            args: {
                id: {
                    type: GraphQLNonNull(GraphQLID)
                },
                template: {
                    type: GraphQLString
                },
                variables: {
                    type: GraphQLString
                },
            },
            resolve(parent, args) {
                return Prompt.findByIdAndUpdate(
                    args.id,
                    {
                        $set: {
                            template: args.template,
                            variables: args.variables
                        }
                    },
                    {new: true}
                )
            }
        }
    }
})

module.exports = new GraphQLSchema({
    query: RootQuery,
    mutation
})