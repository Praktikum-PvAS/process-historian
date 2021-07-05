export interface OPCUAConfig {
    host: string;
    sensors: OPCUAAssemblyType[];
    actuators: OPCUAAssemblyType[];
    services: OPCUAAssemblyType[];
}

interface OPCUAAssemblyType {
    id: string;
    attributes: OPCUAAssemblyAttr[];
}

type OPCUAAssemblyAttr = OPCUAAssemblyAttrPoll | OPCUAAssemblyAttrSub;

interface OPCUAAssemblyAttrPoll {
    name: string;
    node_identifier: string;
    namespace: string;
    mode: "poll";
    interval: number;
}

interface OPCUAAssemblyAttrSub {
    name: string;
    nodeId: string;
    namespace: string;
    mode: "subscription";
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