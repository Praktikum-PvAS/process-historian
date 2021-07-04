export interface OPCUAConfig {
    host: string;

    sensors: {
        id: string;
        nodeId: string;
        namespace: string;
        attributes: {
            name: string;
            nodeId: string;
            namespace: string;
            mode: "poll" | "subscription";
            intervall: number;
        }[];
    }[];

    actuators: {
        id: string;
        nodeId: string;
        namespace: string;
        attributes: {
            name: string;
            nodeId: string;
            namespace: string;
            mode: "poll" | "subscription";
            intervall: number;
        }[];
    }[];

    services: {
        id: string;
        nodeId: string;
        namespace: string;
        attributes: {
            name: string;
            nodeId: string;
            namespace: string;
            mode: "poll" | "subscription";
            intervall: number;
        }[];
    }[];
}

export interface ProgramConfig {
    include: ("sensors" | "actuators" | "services")[];
    tripleStore: {
        host: string;
        username?: string;
        password?: string;
    };
    influxdb: {
        host: string;
        token: string;
        organization: string;
        bucket: string;
    };
    buffer: {
        size: number;
    };
}